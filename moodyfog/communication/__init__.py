'''
Created on 07 feb 2019

@author: mar

Communication package for the fog project
It's just a simple implementation of a MQTT client, for testing purposes.
A nice future development would entail adding a hierarchical structure of topics to differentiate the
analysis based on the elaboration done at earlier stages in the Mist network.

'''

import time
import logging
import json
import pyaudio
from enum import Enum
from paho.mqtt.client import Client
from threading import  Thread

from ..utility.log import Logger
from ..audio.structures import ChunkWindow, AudioChunk
from ..utility import tmr_decide, ObservableDict, Observer


'''

Connection settings

'''

MAX_ATTEMPTS = 5
WAIT_TO_RECONNECT = 5 #sec
TMR_ACTIVE = False


logger = Logger( __name__ )

FOG_ID = 0
INT_TOPICS = ("+/audio/+", "+/light/+", "+/temperature/+", "+/humidity/+", "+/presence/+", "+/photo/+")
EXT_TOPIC = "+/action"



class MQTTClient():

    def __init__( self, client_id ):
        self.client = Client( client_id )
        self.logger = logging.getLogger( __name__ )
        self.client_id = client_id

        '''

        Redefining MQTT client callbacks

        '''

        def on_disconnect( client, userdata, rc ):
            self.logger.info("{} disconnected from the broker!".format( str ( self.client._client_id ), "UTF-8" ) )

        self.client.on_disconnect = on_disconnect

    '''

    Adding the retry feature to the connect method

    '''

    def connect ( self, host, port = 1883 ):
        '''

        The subscriber tries to connect to the broker
        if it's not successful it will retry for a maximum of MAX_ATTEMPTS times

        '''
        attempts = 0

        while attempts < MAX_ATTEMPTS :

            try:
                self.logger.info ( "{} connecting to the broker...attempt number {}".format ( self.client_id, attempts+1 ) )
                self.client.connect( host = host, port = port )

            except ConnectionError:
                time.sleep( WAIT_TO_RECONNECT )
                attempts += 1
                continue

            break

        if attempts == MAX_ATTEMPTS:
            self.logger.error ( "Couldn't connect to the broker!" )
            raise ConnectionError


    def disconnect( self ):
        self.client.disconnect()



    def listen(self):

        def task():
            running = True
            try:
                self.client.loop_start()
                while running:
                    time.sleep(0.1)

            except KeyboardInterrupt :
                running = False
                self.client.loop_stop()
                self.client.disconnect()

        thread = Thread( target = task )
        thread.start()

class InternalCommunicator( MQTTClient, Observer ):

    def __init__( self, client_id, table ):
        super().__init__( client_id )
        self.table = table
        self.audio_tmr = dict()
        self.window = ChunkWindow()


        def on_connect( client, userdata, flags, rc ):
            self.logger.info("{} successfully connected to the broker!".format( str( self.client._client_id.decode()), "UTF-8" ) )

            for topic in INT_TOPICS:
                self.client.subscribe( topic, qos = 0 )


        def on_message ( client, userdata, message ):
            res_area_id, data_type, sensor_id = message.topic.split("/")
            self.logger.info( "Data received from sensor {}, data type: {}, window size: {}".format( sensor_id, data_type, str(len(self.window)) , "UTF-8" ) )

            chunk = AudioChunk( message.payload, pyaudio.paInt32 )
            self.window.append( chunk )

            if res_area_id not in self.table.keys():
                self.table[ res_area_id ] = dict()

            if len( self.window ) >= 80:
                self.table[ res_area_id ][ data_type ] = self.window.audio_type(0.9, -55.4, 3)
                self.window = ChunkWindow()
            else:
                print("como")


        self.client.on_connect = on_connect
        self.client.on_message = on_message

    def update( self, updated_data ):
        self.client.publish( topic = "{}/actuator".format( updated_data[0] ), payload = updated_data[1], qos = 0 )


class ExternalCommunicatorMQTT ( MQTTClient, Observer ):

    def __init__( self, client_id, table ):
        super().__init__( client_id )
        self.table = table

        def on_connect( client, userdata, flags, rc ):
            self.logger.info("{} successfully connected to the broker!".format( self.client._client_id.decode(), "UTF-8" ) )
            self.client.subscribe( EXT_TOPIC, qos = 0 )

        def on_message ( client, userdata, message ):
            area = message.topic.split("/")[0]
            self.logger.info( "Data received from neural network, situation described: {}, in area: {}".format( message.payload.decode(), area, "UTF-8" ) )
            self.table[ area ] = message.payload

        self.client.on_connect = on_connect
        self.client.on_message = on_message

    def update( self, updated_data ):
        self.client.publish( topic = "neural/{}/{}".format( FOG_ID, list( updated_data.keys() )[0] ), payload = json.dumps( updated_data[list( updated_data.keys())[0]] ), qos = 0 )
