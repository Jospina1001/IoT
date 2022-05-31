import paho.mqtt.client as mqtt
import sqlite3
from time import time

MQTT_ADDRESS = '192.168.34.38'
MQTT_USER = 'cbas'
MQTT_PASSWORD = '1234'
MQTT_TOPIC = 'data/+/+'

DATABASE_FILE = 'data.db'

count=0
inf1=''
inf2=''
inf3=''
inf4=''

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    global count
    global inf1
    global inf2
    global inf3
    global inf4
    db_conn = userdata['db_conn']
    sql = 'INSERT INTO data (temperatura, humedad, presion, altitud) VALUES (?, ?, ?, ?)'
    cursor = db_conn.cursor()

    data=str(msg.payload)
    if 'Temperatura:'in data:
         first=data.find(':')
         final=data.find('C')
         inf1=data[first+1:final]
         print('T:',inf1)
         count=count+1
    elif 'Humedad:'in data:
         first=data.find(':')
         final=data.find('%')
         inf2=data[first+1:final]
         print('H:',inf2)
         count=count+1
    elif 'Presion:'in data:
         first=data.find(':')
         final=data.find('hPa')
         inf3=data[first+1:final]
         print('P:',inf3)
         count=count+1
    elif 'Altitud:'in data:
         first=data.find(':')
         final=data.find('mts')
         inf4=data[first+1:final]
         print('A:',inf4)
         count=count+1
    if count == 8:
         cursor.execute(sql,(inf1,inf2,inf3,inf4))
         db_conn.commit()
         cursor.close()
         count=0

def main():

    db_conn = sqlite3.connect(DATABASE_FILE)
    sql ="""
    CREATE TABLE IF NOT EXISTS data (
        temperatura TEXT NOT NULL,
        humedad TEXT NOT NULL,
        presion TEXT NOT NULL,
        altitud TEXT NOT NULL
    )
    """
    cursor = db_conn.cursor()
    cursor.execute(sql)
    cursor.close()

    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.user_data_set({'db_conn': db_conn})

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('INICIO')
    main()