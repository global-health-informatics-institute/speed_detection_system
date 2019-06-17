
# Import time, decimal, serial, GPIO, reg expr, sys, and pygame modules
import os
import sys
import time
import random
#from time import *
from decimal import *
import serial
import RPi.GPIO as GPIO
import re

# Initialize the USB port to read from the OPS-241A module
ser = serial.Serial(
    port = '/dev/ttyACM0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1,
    writeTimeout = 2
)

# Initialize all GPIO pins needed
segment_latch = 7
segment_clock = 16
segment_data1 = 18
segment_data2 = 23
segment_data3 = 24
segment_data4 = 25
segment_data5 = 12
segment_data6 = 13
segment_data7 = 26
segment2_data1 = 6
segment2_data2 = 4
segment2_data3 = 8
segment2_data4 = 27
segment2_data5 = 22
segment2_data6 = 17
segment2_data7 = 5
pin=''
#segment2_data = 29

speed_max = 0.0
start_time = time.clock()
delta_time = 0.0

# Ops241A module settings:  mph, dir off, 20Ksps, min -9dB pwr, squelch 5000
Ops241A_Speed_Output_Units = 'US'
Ops241A_Direction_Control = 'Od'
Ops241A_Sampling_Frequency = 'S2'
Ops241A_Transmit_Power = 'PX'
Ops241A_Threshold_Control = 'QI'
Ops241A_Module_Information = '??'
Ops241A_Data_Accuracy = 'F1'


def main():
    print("Started speed detection application")
    initialize()
    while True:
        
        detect_speed()

        GPIO.cleanup()
        print("Concluded speed detection application")


def initialize():
    print("Initializing variables")
    GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

  #  Configure GPIO output and input channels
    GPIO.setup(segment_latch, GPIO.OUT)
    GPIO.setup(segment_clock, GPIO.OUT)
    GPIO.setup(segment_data1, GPIO.OUT)
    GPIO.setup(segment_data2, GPIO.OUT)
    GPIO.setup(segment_data3, GPIO.OUT)
    GPIO.setup(segment_data4, GPIO.OUT)
    GPIO.setup(segment_data5, GPIO.OUT)
    GPIO.setup(segment_data6, GPIO.OUT)
    GPIO.setup(segment_data7, GPIO.OUT)
    GPIO.setup(segment2_data1, GPIO.OUT)
    GPIO.setup(segment2_data2, GPIO.OUT)
    GPIO.setup(segment2_data3, GPIO.OUT)
    GPIO.setup(segment2_data4, GPIO.OUT)
    GPIO.setup(segment2_data5, GPIO.OUT)
    GPIO.setup(segment2_data6, GPIO.OUT)
    GPIO.setup(segment2_data7, GPIO.OUT)
    #GPIO.setup(pin,GPIO.OUT)
    
    #ser.flushInput()
    #ser.flushOutput()

    # Initialize radar
    initialize_radar_board()

    # Reset serial connection
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.01,
        writeTimeout=2
    )
    # Start radar board


def initialize_radar_board():
    # Initialize and query Ops241A Module
    print("\nInitializing Ops241A Module")
    send_serial_cmd("\nSet Speed Output Units: ", Ops241A_Speed_Output_Units)
    send_serial_cmd("\nSet Direction Control: ", Ops241A_Direction_Control)
    send_serial_cmd("\nSet Sampling Frequency: ", Ops241A_Sampling_Frequency)
    send_serial_cmd("\nSet Transmit Power: ", Ops241A_Transmit_Power)
    send_serial_cmd("\nSet Threshold Control: ", Ops241A_Threshold_Control)
    send_serial_cmd("\nSet Data Accuracy: ", Ops241A_Data_Accuracy)
    send_serial_cmd("\nModule Information: ", Ops241A_Module_Information)


def detect_speed():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    speed_max = 0.0
    delta_time = 0.0
    print("Detecting speed")
# Check for speed info from OPS241-A
    speed_available = False
    Ops241_rx_bytes = ser.readline()
    Ops241_rx_bytes_length = len(Ops241_rx_bytes)
    if (Ops241_rx_bytes_length != 0) :
            Ops241_rx_str = str(Ops241_rx_bytes)
            if Ops241_rx_str.find('{') == -1 :
                # Speed data found
                Ops241_rx_float = float(Ops241_rx_bytes)
                speed_available = True
    if speed_available == True :
            print('speed is:', Ops241_rx_float)
            speed =int(abs(Ops241_rx_float))
            if   speed > 99 :
                 speed = 99
                 for x in range (0, 2) :
                 	speed /= 10
            show_speed(speed)
            if Ops241_rx_float > speed_max :
                speed_max = Ops241_rx_float
                show_speed(Ops241_rx_float)
                start_time = time.clock()
                current_time = start_time
            else :
                display_max_speed_time = 1
                start_time = time.clock()
                delta_time = 0.0
                current_time = time.clock()
                delta_time = current_time - start_time
                if delta_time > display_max_speed_time :
                    show_speed(Ops241_rx_float)
                    speed_max = Ops241_rx_float
                    start_time = time.clock()
                    current_time = start_time
    else :
            reset_speed_time = 5
            start_time = time.clock()
            delta_time = 0.0
            current_time = time.clock()
            delta_time = current_time - start_time
            # Reset speed limit to zero if no motion detected after reset_speed_time
            if delta_time > reset_speed_time :
                print('no speed detected, resetting to 0')
                show_speed(0)
                start_time = time()
                current_time = start_time
   
    #speed = random.randint(0, 99)
    


def show_speed(speed):
    initialize()
    speed = int(round(speed))
    #GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    print("displaying value " + str(speed) + " on seven segment display")
    speedchars = list(str(speed))
    speedchars.reverse()
    digit_length = len(speedchars)
    i=0
    t=0

    if speed > 40 :
        while t < 5:
            while i < digit_length:
                show_on_display(speedchars[i], (i + 1))
                i +=1
                time.sleep(1)
                turn_pins_on_off([],[segment_data1,segment_data2,segment_data3,segment_data4,segment_data5,segment_data6,segment_data7,segment2_data1,segment2_data2,segment2_data3,segment2_data4,segment2_data5,segment2_data6,segment2_data7])
                t += 1

    else:
        while i < digit_length:
            show_on_display(speedchars[i], (i + 1))
            i +=1
            time.sleep(3)
            turn_pins_on_off([],[segment_data1,segment_data2,segment_data3,segment_data4,segment_data5,segment_data6,segment_data7,segment2_data1,segment2_data2,segment2_data3,segment2_data4,segment2_data5,segment2_data6,segment2_data7])

def show_on_display(digit, display):
    if display == 1:
        print("Show " + str(digit) + " on display 1")
        pins = {
            '1': [segment2_data2,segment2_data3],
            '2': [segment2_data1,segment2_data2,segment2_data7,segment2_data5,segment2_data4],
            '3': [segment2_data1,segment2_data2,segment2_data7,segment2_data3,segment2_data4],
            '4': [segment2_data3,segment2_data2,segment2_data6,segment2_data7],
            '5': [segment2_data1,segment2_data6,segment2_data7,segment2_data3,segment2_data4],
            '6': [segment2_data1,segment2_data6,segment2_data7,segment2_data3,segment2_data4,segment2_data5],
            '7': [segment2_data1,segment2_data2,segment2_data3],
            '8': [segment2_data1,segment2_data2,segment2_data3,segment2_data4,segment2_data5,segment2_data6,segment2_data7],
            '9': [segment2_data1,segment2_data2,segment2_data3,segment2_data4,segment2_data6,segment2_data7],
            '0': [segment2_data1,segment2_data2,segment2_data3,segment2_data4,segment2_data5,segment2_data6]
        }
        turn_pins_on_off(pins.get(digit, []), [])

    elif display == 2:
        print("Show " + str(digit) + " on display 2")
        pins = {
            '1':[segment_data2,segment_data3],
            '2':[segment_data1,segment_data2,segment_data7,segment_data5,segment_data4],
            '3':[segment_data1,segment_data2,segment_data7,segment_data3,segment_data4],
            '4':[segment_data3,segment_data2,segment_data6,segment_data7],
            '5':[segment_data1,segment_data6,segment_data7,segment_data3,segment_data4],
            '6':[segment_data1,segment_data6,segment_data7,segment_data3,segment_data4,segment_data5],
            '7':[segment_data1,segment_data2,segment_data3],
            '8':[segment_data1,segment_data2,segment_data3,segment_data4,segment_data5,segment_data6,segment_data7],
            '9':[segment_data1,segment_data2,segment_data3,segment_data4,segment_data6,segment_data7],
            '0':[segment_data1,segment_data2,segment_data3,segment_data4,segment_data5,segment_data6]

        }
        turn_pins_on_off(pins.get(digit, []), [])

    else:
        print("show " + str(digit) + " on display 3")


def turn_pins_on_off(turn_on, turn_off):
    
    for pin in turn_on:
        GPIO.output(pin, True)
       
    for pin in turn_off:
        GPIO.output(pin, False)
       

# sendSerialCommand: function for sending commands to the OPS-241A module
def send_serial_cmd(descrStr, commandStr) :
    data_for_send_str = commandStr
    data_for_send_bytes = str.encode(data_for_send_str)
    print(descrStr, commandStr)
    ser.write(data_for_send_bytes)
    # Initialize message verify checking
    ser_message_start = '{'
    ser_write_verify = False
    # Print out module response to command string
    while not ser_write_verify :
        data_rx_bytes = ser.readline()
        data_rx_length = len(data_rx_bytes)
        if (data_rx_length != 0) :
            data_rx_str = str(data_rx_bytes)
            if data_rx_str.find(ser_message_start) :
                print(data_rx_str)
                ser_write_verify = True

# This defines which function will be executed first
if __name__ == "__main__":
    main()
