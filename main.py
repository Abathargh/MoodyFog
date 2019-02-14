'''

Created on 07 feb 2019

@author: mar

The list of topics is given and static in this testing implementation of the fog architecture.
A series of dictionaries containing the readings of the sensors are initialized; each value can be accessed
with the keys being the topics.

In a real life context, there should be as many dictionary as areas connected to the fog; if we consider an average house
to have 4 rooms, the fog would end up having to deal with a number of dictionaries equal to 4 times the number of houses.

In this testing implementation, we consider a simpler scenario in which there's only a house and only an area in the house
to analyze an actuate.


The logic architecture of the fog node is as follows:

 ____________________
|                    |
|    Forwarding      |
|   (Simplified)     |
|____________________|
         
          |
          |
 ____________________
|                    |
|    Aggregation     |
| (Dictionary/Tables)|
|____________________|
         
          |
          |
 ____________________
|                    |
|   Communication    |
| (MQTT Subscriber)  |
|____________________|



'''

from moodyfog import communication, utility
from moodyfog.communication import MQTTClient, ExternalCommunicator
from moodyfog.utility import TableHandler

from pkg_resources import Requirement, resource_filename
import configparser
import time


TOPICS = ( "audio", "light", "temperature", "humidity", "presence", "photo" )
area_table = dict()



if __name__ == "__main__" :
    
    config = configparser.ConfigParser()

    try :
        if len ( config.read ( "./moodyfog/fog.conf" ) ) == 0 :
            config.read ( resource_filename ( Requirement.parse ( "Moody" ), "moody.conf" ) )
        
    except :
        raise ( "An error occurred while importing the default configuration!" )
    
    BROKER_ADDRESS = config["Communication"]["BROKER_ADDRESS"]
    BROKER_PORT = int ( config["Communication"]["BROKER_PORT"] )
    
    communication.logger.console ( True )
    utility.logger.console ( True )

    
    external_communicator = ExternalCommunicator()
    
    table_handler = TableHandler( external_communicator )
    
    mqtt_client = MQTTClient( table_handler )
   
    try:    
        mqtt_client.connect( host = BROKER_ADDRESS, port = BROKER_PORT )
    
    except:
        print( "Error attempting to connect")    
    
    def on_message ( client, userdata, message ):
    
        res_area_id, data_type, sensor_id = message.topic.split("/")
        
        print( "Data received from sensor {}, data type: {}, payload: {}".format( sensor_id, data_type, message.payload.decode() , "UTF-8" ) )
        table_handler.update( res_area_id, data_type, message.payload )
        
    mqtt_client.on_message = on_message
                
    
    try:
        mqtt_client.loop_start()
        while True: 
            time.sleep(0.1)
            
    except KeyboardInterrupt :
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
