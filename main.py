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
import argparse
import moodyfog.communication, moodyfog.utility

from pkg_resources import Requirement, resource_filename
import configparser


TOPICS = ( "audio", "light", "temperature", "humidity", "presence", "photo" )
area_table = dict()



if __name__ == "__main__" :
    
    parser = argparse.ArgumentParser()
    parser.add_argument ( "--verbose", "-v", help = "If the verbose option is selected, the program prints informations about the energy level of every analyzed frame", action = "store_true" )
    args = parser.parse_args()

    if args.verbose:
        moodyfog.communication.logger.console ( True )
        moodyfog.utility.logger.console ( True )
        
    config = configparser.ConfigParser()

    try :
        if len ( config.read ( "/home/pi/Tesi/MoodyFog/moodyfog/fog.conf" ) ) == 0 :
            config.read ( resource_filename ( Requirement.parse ( "Moody" ), "moody.conf" ) )
        
    except :
        raise ( "An error occurred while importing the default configuration!" )
    
    BROKER_ADDRESS = config["Communication"]["BROKER_ADDRESS"]
    BROKER_PORT = int ( config["Communication"]["BROKER_PORT"] )
    

    moodyfog.connect( BROKER_ADDRESS, BROKER_PORT )
    moodyfog.start_listening()
    
    

