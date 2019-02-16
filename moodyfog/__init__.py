'''

Created on 15 feb 2019

@author: mar

Façade module for the fog project.

'''
import logging
from paho.mqtt.client import Client

from .utility import Observer, ObservableDict, ObservableMultidimensionalDict
from .communication import InternalCommunicator, ExternalCommunicatorMQTT
from .utility.log import Logger


areas_table = ObservableMultidimensionalDict()
areas_actions = ObservableDict()


#Inizializzazione connessioni 

internal_communicator = InternalCommunicator( "Fog_1_int", areas_table )
external_communicator = ExternalCommunicatorMQTT( "Fog_1_ext", areas_actions )

areas_table.set_observer( external_communicator )
areas_actions.set_observer( internal_communicator )


def connect( host, port ):
    internal_communicator.connect( host, port )
    external_communicator.connect( host, port )
def start_listening():
    internal_communicator.listen()
    external_communicator.listen()

