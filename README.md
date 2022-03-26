# mqtt-mysql-bridge
Easy MQTT-MySQL bridge

## Introduction

This is a simple Python script that just listen for MQTT messages and, if source device is included in the list, insert event and payload to a MySQL database

I've created this simple bridge to save MQTT messages produced by my sensors to a MySQL DB, binding to my Mosquitto server.

It's just a basic script: feel free to modify and improve it!