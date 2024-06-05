import network
import time
from machine import Pin
import dht
import urequests as requests
from umail.smtp import SMTP
import ntptime
import utime

# Configurações de WiFi
WIFI_SSID = 'esp32'
WIFI_PASSWORD = 'esp32teste'

# Configurações do bot do Telegram
BOT_TOKEN = '7349649805:AAFG9dswKsZLfC0qvrB6FywbMlAPnza8Fic'
GROUP_CHAT_ID = '-1002212482887'

# Configurações do sensor DHT
DHT_PIN = 4
sensor = dht.DHT11(Pin(DHT_PIN))

# Configurações de E-mail
EMAIL_SENDER_ACCOUNT = 'dadostemperatura@gmail.com'
EMAIL_SENDER_PASSWORD = 'xkto ecys ulfw vnzp'
EMAIL_RECIPIENT = 'esp32cloud@gmail.com'
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465

# Limite de temperatura para enviar alerta imediato
TEMPERATURE_LIMIT = 25.0

# Horários específicos para envio (horas e minutos)
SCHEDULED_TIMES = [(8, 0), (14, 0), (20, 0)]


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
        print("Conectando ao WiFi...")
    print("Conectado ao WiFi:", wlan.ifconfig())
    ntptime.settime()


def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': GROUP_CHAT_ID,
               'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso para o Telegram!")
        else:
            print(
                f"Falha ao enviar a mensagem para o Telegram: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")


def send_email(subject, message):
    smtp = SMTP(SMTP_HOST, SMTP_PORT, ssl=True)
    smtp.login(EMAIL_SENDER_ACCOUNT, EMAIL_SENDER_PASSWORD)
    smtp.to(EMAIL_RECIPIENT)
    smtp.write("From: {}\n".format(EMAIL_SENDER_ACCOUNT))
    smtp.write("Subject: {}\n".format(subject))
    smtp.write("Content-Type: text/html\n")
    smtp.write("\n")
    smtp.write(message)
    try:
        smtp.send()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar o e-mail: {e}")
    smtp.quit()


def check_temperature():
    try:
        sensor.measure()
        temperature = sensor.temperature()
        print('Temperatura lida: {}°C'.format(temperature))

        current_time = utime.localtime()
        current_hour = current_time[3]
        current_minute = current_time[4]

        for hour, minute in SCHEDULED_TIMES:
            if current_hour == hour and current_minute == minute:
                send_telegram_message(f"🌡️ *Temperatura*: {temperature}°C")
                send_email("Alerta de Temperatura",
                           f"<div style='color:#2C3E50;'><h1>Dados de Temperatura</h1><p>🌡️ <b>Temperatura</b>: {temperature}°C</p></div>")

        if temperature > TEMPERATURE_LIMIT:
            alert_message = f"🚨 *Alerta de Temperatura*: {temperature}°C (Acima do limite!)"
            send_telegram_message(alert_message)
            send_email("Alerta de Temperatura",
                       f"<div style='color:#2C3E50;'><h1>Alerta de Temperatura</h1><p>🚨 <b>Temperatura</b>: {temperature}°C (Acima do limite!)</p></div>")
    except OSError as e:
        print('Falha ao ler do sensor DHT!')


def main():
    connect_to_wifi()
    while True:
        check_temperature()
        time.sleep(60)  # Verificar a temperatura a cada minuto


if __name__ == '__main__':
    main()
