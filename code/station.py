##############################################IMPORTATION DES BIBLIOTHEQUES##############################################
from grovepi import *
from grove_rgb_lcd import *
import time,datetime,json
from math import *
#from azure.servicebus import ServiceBusService
#from azure.servicebus import Message
###########################################DECLARATION DES CONSTANTES GLOBALES###########################################
dht_sensor_port = 7 #capteur humidite et temperature (DHT11 ou DHT22) sur D7
dht_sensor_type = 0 #mettre 0 si bleu (DHT11) ou 1 si blanc (DHT22)
t_actuator = 799 #nombre de loop entre deux envoie de donnees
t_wait = 30
lum_seuil = 10 #seuil au dessus du quel on determine la lumiere comme allume
lum_sensor = 1 #capteur de lumiere sur A1
potentiometer = 2 #bouton de menu sur A2
##########################################ACTIVATION DES PORTS DU SHIELD GROVEPI#########################################
####################################################VARIABLES INTERNES###################################################
t_refresh = 800 # nombre de loop entre deux envoie a l instant t
compteur_echec_envoie = 0 # compteur d echec d envoie de donnee sur azure (se remet a 0 si reussite)
mode_value = 0 # les deux valeurs permette d eviter une actualisation inutile de l ecran qui le faisait clignoter
mode_value_old = 0
##############################################VARIABLES DE DONNEES ENVOYEES##############################################
temp = 0
hum = 0
lum = 0
lum_statut = False
identifiant = "Identifiant" # a modifier
lum_envoie = 0
########################################################FONCTIONS########################################################
def DHT() : #temperature et humidite numerique
    global temp,hum
    [temp,hum] = dht(dht_sensor_port,dht_sensor_type)
    temp = round(temp,1)

def Luminosite() : #luminosite qui envoie True ou False avec le seuil
    global lum_statut,lum_envoie
    lum_value = analogRead(lum_sensor)
    try :
        resistance = (float)(1023 - lum_value)*10/lum_value
        if resistance > lum_seuil :
            lum_statut = False
            lum_envoie = 0
        else :
            lum_statut = True
            lum_envoie = 1
    except : #si erreur au capteur, il va alterner true et false pour que cela soit visible 
        if lum_statut :
            lum_statut = False
            lum_envoie = 0
        else : 
            lum_statut = True
            lum_envoie = 1

def screen_administrator() : # permet de gerer lecran sans quil refresh a chaque iteration 
    global mode_value
    mode_value_old = mode_value
    if (encoder_value <=341 and encoder_value >= 0) and mode_value != 1 : #MODE 1
       	setText("Temperature : \n" +str(temp))
       	setRGB(0,128,255)
       	mode_value = 1
    elif (encoder_value <= 682 and encoder_value > 341) and mode_value != 2 : #MODE 2
       	setText("Humidite : \n"+str(hum))
       	setRGB(255,0,128)
       	mode_value = 2
    elif (encoder_value > 682 and encoder_value <=1023) and mode_value != 3 : # MODE 3
        if lum_statut :
            text = 'Allumee'
        else : 
            text = 'Eteinte'
       	setText("Lumiere \n"+text)
       	setRGB(255,128,0)
       	mode_value = 3   
    if not ((mode_value - mode_value_old) != 0) : #s il y a pas eu un changement de mode sur l ecran
        time.sleep(140.0/1000.0) #on attend 140 ms pour etre sur du temps a chaque loop


#def createSBS() : #permet de creer le canal de communication avec Azure 
	
#    service_namespace = 'namespaceName' #a modifier
#    key_name = 'SharedAccessKeyName' # a modifier
#    key_value = 'SharedAccessKey' # a modifier
	
#    sbs = ServiceBusService(service_namespace, shared_access_key_name=key_name, shared_access_key_value=key_value)

#    return sbs
##########################################################SETUP##########################################################
#sbs = createSBS()
setText("Bienvenue\ndans l'IoT Hub")
setRGB(128,255,0)
time.sleep(2)
######################################################BOUCLE INFINI######################################################


while True :
    if ( t_refresh >= t_actuator) :
        Luminosite()
	DHT()
	while (isnan(temp) or temp == 0) : # on essaie tant que le capteur n a pas de valeur valide
	    DHT()
        dt = str(datetime.datetime.now())
        d = {'DeviceID' : identifiant,'Time' : "France/Local Time here",'Temperature' : temp, 'Humidity' : hum,'Light' : lum_envoie }
        msg = json.dumps(d) #cree le message a envoyer
        try :
            #sbs.send_event('eventHubName',msg) #a modifier
            compteur_echec_envoie = 0
        except :
            compteur_echec_envoie += 1
            if compteur_echec_envoie == 720 : #echec d envoie de message depuis 24h
                setRGB(255,0,0)
		setText("Probleme envoie\nmessage azure")
		break # sort de la boucle, reboot necessaire du programme ou de la RPI
        t_refresh = 0

    if (t_refresh >= t_wait) : # on attend un peu avant de refresh l ecran
        encoder_value = analogRead(potentiometer)
        screen_administrator()
    t_refresh += 1
