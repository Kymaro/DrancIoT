#!/usr/bin/env python
# -*- coding: utf-8 -*-

from grovepi import *
from grove_rgb_lcd import *
import time
from math import *


dht_sensor_port = 7
dht_sensor_type = 0

temp_sensor = 0
lum_sensor = 1

button = 3
led = 4

pinMode(button,"INTPUT")
pinMode(led,"OUTPUT")

t_refresh = time.time() #on ne met pas les 5 minutes de plus pour réaliser la relève des capteurs une première fois
temp_dht = 0
hum = 0
temp = 0 
button_value = 0
lum = 0

setText("Bienvenue\ndans l'IoT Hub")
setRGB(128,255,0)

While True :

#    if (time.time() >= t_refresh) : #si on a dépassé les 5 minutes
    DHT()
    temperature()
    print(temp_dht)
    print(hum)
    print(temp)
    #t_refresh = time.time() + 60*5 #on met à jour la valeur de t_refresh pour la prochaine actualisation
    time.sleep(1)

        


"""
But du programme :

    Prendre les valeurs toutes les 5 minutes par une variable t_refresh = time.time() + 60*5
    Dans while true, un if time.time() > t_refresh ==> on refresh les valeurs
    Ensuite on gère l affichage selon la valeur définie par le bouton.

    Dans le if du refresh, on mettra aussi le code pour envoyer les valeurs dans le hub azure

A priori, on a fait le tour

https://docs.microsoft.com/fr-fr/azure/iot-hub/iot-hub-python-getstarted
"""

def DHT() :
    [temp_dht,hum] = dht(dht_sensor_port,dht_sensor_type)

def temperature() :
    temp = temp(temp_sensor,'1.2')
