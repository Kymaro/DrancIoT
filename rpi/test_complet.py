from grovepi import *
from grove_rgb_lcd import *
import time,datetime,json
from math import *
from util import *

"""
TO DO :
    * ajout capteur luminosit
    * faire tourner 24h les capteurs pour vrifier les valeurs
    * avoir un capteur de temprature extrieur pour vrifier les valeurs (semble haute)
    * changer DevideID par un string qui permet dentifier la RPI pour ensuite retrouver les graphiques sur le portail azure.
"""

dht_sensor_port = 7
dht_sensor_type = 0

temp_sensor = 0
lum_sensor = 1
potentiometer = 2

button = 3
led = 4

B=4250
R0 = 100000

ID = getId()
sbs = createSBS()

pinMode(button,"INTPUT")
pinMode(led,"OUTPUT")
pinMode(temp_sensor,"INTPUT")
pinMode(potentiometer,"INPUT")
pinMode(lum_sensor,"INTPUT")
time.sleep(1)

t_refresh = 6000
t_actuator = 799
t_wait = 50
compteur_echec_envoie = 0

temp_dht = 0
hum = 0
tempe = 0 
mode_value = 0
mode_value_old = 0
lum = 0


adc_ref = 5
grove_vcc = 5
full_angle = 300

setText("Bienvenue\ndans l'IoT Hub")
setRGB(128,255,0)
time.sleep(2)

def DHT() : #temperature et humidite analogique
    global temp_dht,hum
    [temp_dht,hum] = dht(dht_sensor_port,dht_sensor_type)
    temp_dht = round(temp_dht,1)

def Temperature() : #capteur de temperature analogique
    global tempe
    analog_value = analogRead(temp_sensor)
    R = 1023.0/analog_value - 1.0
    tempe = 1.0/(log(R)/B + 1/298.15) - 273.15
    tempe= round(tempe,1)

def PotentiometerToDegrees(potentiometer_value) : #convertie la valeur du potentiometre en degree
    voltage = round((float)(potentiometer_value)*adc_ref / 1023,2)
    degrees = round((voltage*full_angle)/grove_vcc,2)
    return degrees

def screen_administrator() : # permet de gerer lecran sans quil refresh a chaque iteration 
    global mode_value
    encoder_value = analogRead(potentiometer)
    mode_value_old = mode_value
    if mode_value == 4 : #si echec envoie message pendant 24h on change l affichage local pour avertir
        setRGB(255,0,0)
        setText("Probleme envoie\nmessage azure")
    if (encoder_value <=341 and encoder_value >= 0) and mode_value != 1 : #MODE 1
       	setText("Temperature : \n" +str((tempe + temp_dht)/2.0))
       	setRGB(0,128,255)
       	mode_value = 1
    elif (encoder_value <= 682 and encoder_value > 341) and mode_value != 2 : #MODE 2
       	setText("Humidite : \n"+str(hum))
       	setRGB(255,0,128)
       	mode_value = 2
    elif (encoder_value > 682 and encoder_value <=1023) and mode_value != 3 : # MODE 3
       	setText("Luminosite \n")
       	setRGB(255,128,0)
       	mode_value = 3   
    if not ((mode_value - mode_value_old) != 0) : #s il y a pas eu un changement de mode sur l ecran
        time.sleep(140.0/1000.0) #on attend 140 ms pour etre sur du temps a chaque loop

while True :
    if ( t_refresh >= t_actuator) : 
    	Temperature()
	DHT() #A faire en dernier car un delai de retour de valeur digital
	while (isnan(temp_dht) or temp_dht == 0) : #si jamais le capteur foire au releve
		DHT()
    	#print(temp_dht)
    	#print(hum)
    	#print(tempe)
        average_temp = (temp_dht + tempe)/2.0
	average_temp = round(average_temp,1)
	t_refresh = 10 
	identifiant = "Rpi Test"
        dt = str(datetime.datetime.now())
        d = {'DeviceID' : identifiant, 'Temperature' : average_temp, 'Humidity' : hum,'Time' : dt }
        msg = json.dumps(d)
        #print(msg)
        try :
            sbs.send_event('dht11',msg)
            compteur_echec_envoie = 0
        except :
            compteur_echec_envoie += 1
            if compteur_echec_envoie == 720 : #echec d envoie de message depuis 24h
                mode_value = 4
    if (t_refresh >= t_wait) : # on attend un peu avant de refresh l ecran car valeur aberante de l encoder quand on regarde les autres capteur
        screen_administrator()
    t_refresh += 1

"""
https://docs.microsoft.com/fr-fr/azure/iot-hub/iot-hub-python-getstarted
http://www.stevenfowler.me/p/send-raspberry-pi-data-azuure/
http://www.instructables.com/id/Sending-Temperature-Sensor-Data-to-Azure-Database/

login azure cli : "azure login"

temps d'excecution des loop :

    si actualisation : 1 loop = 450ms
    sinon : 150 ms

    
"""
