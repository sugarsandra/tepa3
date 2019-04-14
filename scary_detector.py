#! /usr/bin/env python
# -*- coding: utf-8 -*-

# εισαγωγή απαραίτητων modules
import RPi.GPIO as GPIO
import time
import sys
import threading
from subprocess import call
import random
import wave
import contextlib

GPIO.setmode(GPIO.BCM)

# μεταβλητές για τα ηλεκτρονικα εξαρτήματα

TRIG=23                                      
ECHO=18
Servo=25
red = 17
green = 27
blue = 22

#μεταβλητές για τους ήχους
sound = 0                
Lenght = 0.0          # μήκος ήχου

# setup των ηλεκτρονικων εξαρτημάτων
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(Servo,GPIO.OUT)

# setup για το servo
S=GPIO.PWM(Servo,50)    #συχνότητα σε Hz, χρήση της τεχνικης PWM
S.start(0) 

#module κίνησης του servo
def Move_Servo():
        global Length
        time_passed = 0.0
        time_start = 0.0
        time_end = 0.0
        
        while time_passed < Length:           # μέτρηση χρόνου σε σχέση με το μήκος του ήχου
                time_start = time.time()
                S.ChangeDutyCycle(5)  # αλλαγή της πορείας του servo τέρμα αριστερά
                time.sleep(0.5)
                S.ChangeDutyCycle(10) # αλλαγή της πορείας του servo τέρμα δεξιά
                time.sleep(0.5)
                time_end=time.time()
                time_passed = time_passed + (time_end - time_start)
        S.ChangeDutyCycle(0)

# module επιλογής ήχου
def playsounds(i):      
	string = "/home/pi/Desktop/scary/" + i + ".wav"                       # μεταβλητή που αποθηκεύει τον αριθμό του wav αρχείου που θα ακουστεί
	print (string)
	call(["aplay", string])                                               # η εντολή aplay χρησιμοποιείται για να κανουμε ήχους να παίξουν στο ηχείο μας

# σβήσιμο του RGB LED
def off_colors():
	GPIO.output(red, 0)
	GPIO.output(green, 0)
	GPIO.output(blue, 0)
	
# δημιουργία αποχρώσεων στο RGB LED σε σχέση με το μήκος του ήχου
def on_colors():
	global Length            
	turn_on = 0.03                    
	turn_off = 0.03                     
	time_passed = 0.0       # κρατάμε το χρονο που έχει περάσει από την αρχή ήχων και φωτισμού
	time_start = 0.0              # αρχή ήχων και φωτισμού
	time_end = 0.0               # τέλος ήχων  και φωτισμού
	
	while time_passed < Length:                 # όσο ο χρόνος που έχει περάσει ειναι μικρότερος του μήκους του ήχου
		time_start = time.time()     # από το module time οριζουμε την αρχή του χρονου για τις αποχρώσεις
		
		GPIO.output(red, 1)        # το LED ανάβει κόκκινο
		time.sleep(turn_on)
		off_colors()
		time.sleep(turn_off)# 
		
		GPIO.output(green, 1) # το LED ανάβει πράσινο
		time.sleep(turn_on)
		off_colors()
		time.sleep(turn_off)
		
		GPIO.output(blue, 1)# το LED ανάβει μπλε
		time.sleep(turn_on)
		off_colors()
		time.sleep(turn_off)
		
		GPIO.output(red, 1)# το LED αναβει κόκκινο και μπλε
		GPIO.output(blue, 1)
		time.sleep(turn_on)
		off_colors()
		time.sleep(turn_off)
		
		GPIO.output(red, 1)# το LED ανάβει κόκκινο και πράσινο
		GPIO.output(green, 1)
		time.sleep(turn_on)
		off_colors()
		time.sleep(turn_off)
		
		GPIO.output(green, 1)# το LED αναβει πράσινο και μπλε
		GPIO.output(blue, 1)
		time.sleep(turn_on)
		off_colors()
		time.sleep(turn_off)
		
		GPIO.output(red, 1)   # ανάβουν όλα τα χρώματα του LED
		GPIO.output(green, 1)
		GPIO.output(blue, 1)
		time.sleep(turn_on)
		off_colors()
		
		time_end = time.time()# οριζουμε το τέλος του χρόνου
		time_passed = time_passed + (time_end - time_start)# ορίζουμε το χρόνο που έχει περάσει ανά κύκλο αποχρώσεων

# module για αναγνωση του αρχείου ήχου και μέτρηση της διάρκειάς του	
def sound_length(i):                      
	string = "/home/pi/Desktop/scary/" + i + ".wav"                                                
	with contextlib.closing(wave.open(string, 'r')) as echo:               # με το module wave ανοίγει το αρχειο για αναγνωση
                                                                                                                                          # ο context manager στο τέλος θα κλείσει το αρχείο ήχου
		return echo.getnframes() / float(echo.getframerate())  #  επιστρέφει την διάρκεια του αρχείου ήχου

# module ανάγνωσης της απόστασης
def read_distance(pulse_start,pulse_end):
        GPIO.output(TRIG, False)            # stop trigging 
        time.sleep(0.0001)                      
    
        GPIO.output(TRIG, True)              # start  trigging - ξεκιναει την αποστολή ηχητικού κύματος
        time.sleep(0.00001)
        GPIO.output(TRIG,False)
    
        while GPIO.input(ECHO)== 0:
                pulse_start=time.time()                            # υπολογίζει πότε εκπέμφθηκε το ηχητικό κύμα
        while GPIO.input(ECHO)== 1:
                pulse_end=time.time()                            # υπολογίζει πότε επέστρεψε το ηχητικό κύμα
        pulse_duration =pulse_end-pulse_start       # υπολογίζει το χρονικό διάστημα που μας ενδιαφέρει
        distance=pulse_duration * 17150                   # υπολογιζει την απόσταση σε cm
        distance=round(distance,2)
        print( "Η απόσταση είναι: {} cm ".format(distance))
        return distance


# εντολή για την μετατροπή του κειμένου σε φωνητικό μήνυμα κατά την εκκίνηση του προγράμματος
call(['espeak "Welcome to the world of Robots" 2>/dev/null'], shell=True)

try:
        while True:
                if (read_distance(0,0)< 20.00):
                        sound = random.randint(1, 5)
                        Length = sound_length(str(sound))
                        threading.Timer(0, on_colors).start()# ξεκινάει η εκτέλεση του module on_colors άμεσα
                        threading.Timer(0,Move_Servo).start()# ξεκινάει η εκτέλεση του module Move_Servo άμεσα
                        playsounds(str(sound)) # ξεκινάει ο ήχος
except KeyboardInterrupt:
        GPIO.cleanup()
        S.stop()
        sys.exit(0)
except:
        print (sys.exc_info())
finally:
        S.stop()
        GPIO.cleanup()
        sys.exit(0)
