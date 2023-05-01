import RPi.GPIO as GPIO
import time

GPIO_Nbr = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_Nbr, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    if GPIO.input(GPIO_Nbr):
        print("SW On")
        time.sleep(0.5)
GPIO.cleanup()
