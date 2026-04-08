---------------------
#brinde pro professor, teste pra ligar todos os leds e buzzer



import RPi.GPIO as GPIO
import time

# Usando numeração BCM
GPIO.setmode(GPIO.BCM)

LED_VERDE = 18
LED_VERMELHO = 23
BUZZER = 24

GPIO.setup(LED_VERDE, GPIO.OUT)
GPIO.setup(LED_VERMELHO, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

try:
    print("Ligando tudo...")

    GPIO.output(LED_VERDE, True)
    GPIO.output(LED_VERMELHO, True)
    GPIO.output(BUZZER, True)

    time.sleep(5)

    print("Desligando tudo...")

    GPIO.output(LED_VERDE, False)
    GPIO.output(LED_VERMELHO, False)
    GPIO.output(BUZZER, False)

finally:
    GPIO.cleanup()
