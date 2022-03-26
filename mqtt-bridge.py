#!/usr/bin/env python3
#
# MQTT-MySQL bridge
# 
# by Michele <o-zone@zerozone.it> Pinassi
#
import paho.mqtt.client as mqtt
import MySQLdb
from loguru import logger
import configparser
import threading
import argparse
from time import sleep, perf_counter
from queue import Queue
import sys

devicesList = []

####################
#
# db_query(query)
#
#
def db_query(query,args):
    cursor = db.cursor()
    try:
        cursor.execute(query, args)
        db.commit()
        return cursor
    except Exception as e:
        logger.error("SQL error %s"%(e))
        return False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logger.debug("%s: %s"%(msg.topic,str(msg.payload)))

    topics = msg.topic.split('/')
    device = topics[0]
    topics.pop(0)
    topic = '/'.join(topics)

    if device in devicesList:
        queue.put((device,topic,msg.payload))


def mysql_thread(args):
    logger.info("MySQL thread started")

    while True:
        if queue.empty():
            sleep(10.0)
            continue

        (device,topic,payload) = queue.get()

        logger.debug("Push new data for %s/%s"%(device,topic))

        db_query("INSERT INTO events(device, topic, value, add_date) VALUES (%s,%s,%s,NOW())",(device,topic,payload))


def mqtt_thread(args):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    logger.debug("MQTT thread started")
    try:
        client.connect(args["host"], int(args["port"]), 60)
    except Exception as e:
        logger.error("Oh oh! MQTT connection error: %s"%e)
        return False

    logger.debug("MQTT listener is running")
    client.loop_forever()

# MAIN()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQTT-MySQL bridge - A connector between MQTT and MySQL')
    parser.add_argument('-c','--config', help='Configuration file', required=True)
    args = parser.parse_args()

    logger.info("MQTT-MySQL bridge started")

    start_time = perf_counter()

    config = configparser.ConfigParser()
    config.read(args.config)

    assert "mqtt" in config.sections()
    assert "mysql" in config.sections()

    if config["mqtt"]["devices"]:
        for device in config["mqtt"]["devices"].split(","):
            devicesList.append(device.strip())
            logger.info("Added %s to MQTT devices"%device)

    queue = Queue(maxsize = 100)

    try:
        db = MySQLdb.connect(host=config["mysql"]["host"],
                        port=int(config["mysql"]["port"]),
                        user=config["mysql"]["username"],
                        passwd=config["mysql"]["password"],
                        db=config["mysql"]["db"])
    except Exception as e:
        logger.error("Oh oh! MySQL connection error: %s"%e)
        sys.exit()

    # Start MQTT thread
    t_mqtt = threading.Thread(target=mqtt_thread,name="mqtt_thread", args=(config["mqtt"],))
    t_mqtt.start()
    # Start MySQL thread
    t_mysql = threading.Thread(target=mysql_thread, name="mysql_thread", args=(config["mysql"],))
    t_mysql.start()

    t_mqtt.join()
    t_mysql.join()

    end_time = perf_counter()
    logger.info("Bridge ran for %0.2f second(s)"%(end_time - start_time))