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
from enum import Enum
from paho.mqtt.client import Client
from threading import  Thread

from ..utility.log import Logger
from moodyfog.utility import TableHandler


'''

Connection settings

'''

MAX_ATTEMPTS = 5
WAIT_TO_RECONNECT = 1 #sec


logger = Logger( __name__ )

class Communication ( Enum ):
    Socket = 0
    Serial = 1
    MQTT = 2


class MQTTClient ( Client ):
    
    def __init__( self, table_handler ):
        super().__init__( "Subscriber_fog" )
        self.logger = logging.getLogger( __name__ )
        self.table_handler = table_handler
        
    
    
    '''
    
    Overriding some event based callback Client methods
    
    ''' 
    
    @property
    def on_connect ( self ):
        self.logger.info("{} successfully connected to the broker!".format( str( self._client_id, "UTF-8" ) ) )
    
    @property
    def on_disconnect ( self ):
        self.logger.info("{} disconnected from the broker!".format( str ( self._client_id, "UTF-8" ) ) )
    
    @property
    def on_message ( self, client, userdata, message ):
        
        sensor_id, data_type = message.topic.split("/")
        
        self.logger.info( "Data received from sensor {}, data type: {}, payload: {}".format( sensor_id, data_type, message.payload, "UTF-8" ) )
        self.table_handler.update( sensor_id, data_type, message.payload )

    
    
    
    '''
    
    Adding the retry feature to the connect method
    
    '''
        
    def connect ( self, host, port = 1883, keepalive = 60, bind_address = "" ):
        
        '''
        
        The subscriber tries to connect to the broker
        if it's not successful it will retry for a maximum of MAX_ATTEMPTS times
        
        '''
        
        attempts = 0
        
        while attempts < MAX_ATTEMPTS :                                       
            
            try:
                self.logger.info ( "Connecting to the broker... attempt number {}".format ( attempts ) )
                super().connect( host = host, port = port )
            
            except ConnectionError: 
                   
                time.sleep( WAIT_TO_RECONNECT )
                attempts += 1
                continue
            
            break
        
        if attempts == MAX_ATTEMPTS: 
            self.logger.error ( "Couldn't connect to the broker!" )
            raise ConnectionError
        
        

class ExternalCommunicator():

    '''
    
    This class provides a way to communicate with the external service which will analyze the partially elaborated data that has been collected 
    by the Mist network.
    Different ways of handling such communication are given, so that it's easy to switch to different ones in order to test the software in an offline 
    environment.
    
    It also provides a way to listen to the return messages sent by the analysis service (like a Cloud or similar): this communicator acts as both a client and
    a server.
    
    '''
    
    def __init__( self, host, port, strategy =  ):        
        self.host = host
        self.port = port
        
        
        
        