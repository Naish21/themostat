# https://github.com/Naish21/themostat
'''
 * The MIT License (MIT)
 *
 * Copyright (c) 2016 Jorge Aranda Moro
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.

'''

#This part is to connect to the WiFi
#In this case: SSID: TP-LINK_F3D4B2 & PASS: 90546747

WIFISSID='TP-LINK_F3D4B2'
WIFIPASS='90546747'

def do_connect():
    from network import WLAN
    sta_if = WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFISSID, WIFIPASS)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

#---End Wifi Config---

from machine import Pin

led = Pin(2, Pin.OUT, value=1)

#---MQTT Sending---

from time import sleep_ms
from ubinascii import hexlify
from machine import unique_id
#import socket
from umqtt import MQTTClient

SERVER = "192.168.0.101"
CLIENT_ID = hexlify(unique_id())
TOPIC1 = b"/sensor1/tem"
TOPIC2 = b"/sensor1/hum"
TOPIC3 = b"/sensor1/led"

def envioMQTT(server=SERVER, topic="/foo", dato=None):
    try:
        c = MQTTClient(CLIENT_ID, server)
        c.connect()
        c.publish(topic, dato)
        sleep_ms(200)
        c.disconnect()
        #led.value(1)
    except Exception as e:
        pass
        #led.value(0)

state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(0)
        state = 1
    elif msg == b"off":
        led.value(1)
        state = 0

def recepcionMQTT(server=SERVER, topic=TOPIC3):
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(topic)
    #print("Connected to %s, subscribed to %s topic" % (server, topic))
    try:
        c.wait_msg()
    finally:
        c.disconnect()

#---End MQTT Sending---

#---DHT22---
from dht import DHT22

ds = DHT22(Pin(16)) #DHT22 connected to GPIO16

def medirTemHum():
    try:
        ds.measure()
        tem = ds.temperature()
        hum = ds.humidity()
        #ed.value(1)
        return (tem,hum)
    except Exception as e:
        #led.value(0)
        return (-1,-1)

#---End DHT22---

#---OLED 128x64---
from ssd1306 import SSD1306_I2C
from machine import I2C

i2c = I2C(sda = Pin(4), scl = Pin(5))
display = SSD1306_I2C(128, 64, i2c)

def displaytem(tem,hum):
    display.fill(0)
    temperatura = 'Tem: ' + str(tem)[:5] + 'C'
    humedad = 'Hum: ' + str(hum)[:5] + '%'
    display.text(temperatura,2,2,1)
    display.text(humedad,2,14,1)
    display.show()

#---End OLED---


#---Main Program---
sleep_ms(10000)

while True:
    (tem,hum) = medirTemHum()
    displaytem(tem,hum)
    envioMQTT(SERVER,TOPIC1,str(tem))
    envioMQTT(SERVER,TOPIC2,str(hum))
    recepcionMQTT()
    sleep_ms(10000)

#---END Main Program---
