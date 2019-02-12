'''
Created on 02 feb 2019

@author: mar

Table formatter/organizer used to store the data collected by the sensors.
A table is in a 1:1 relation with an area, so there will be as many table as the numbers of area
in the fog jurisdiction.


The areas table structure is as following:

                         ____________________
                        |                    | 
                        |  topic_1 : data_1  |
                        |  topic_2 : data_2  | 
    Sensor_id_1         |         .          |
                        |         .          |
                        |         .          |
                        |  topic_n : data_n  |       
                        |____________________|
                        |                    |
                        |  topic_1 : data_1  |
                        |  topic_2 : data_2  | 
    Sensor_id_2         |         .          |
                        |         .          |
                        |         .          |
                        |  topic_n : data_n  |       
                        |____________________|
         
         .                        .
         .                        .
         .                        .
                         ____________________
                        |                    |
                        |  topic_1 : data_1  |
                        |  topic_2 : data_2  | 
    Sensor_id_n         |         .          |
                        |         .          |
                        |         .          |
                        |  topic_n : data_n  |       
                        |____________________|
                    

'''

import logging

from ..utility.log import Logger
from threading import Lock



logger = Logger( __name__ )



class TableHandler():
    
    def __init__( self, ext_communicator ):        
        self.mutex = Lock()
        self.logger = logging.getLogger( __name__ )
        self.areas_table = dict()
        self.ext_communicator = ext_communicator
        
        self.logger.info( "data table successfully initialized!" )
    
    def update( self, sensor_id, data_type, data ):
        
        sensor_data = sensor_id.split("_")
        area_id = "{}_{}".format( sensor_data[0], sensor_data[1] )
        
        if self.area_tables[ area_id ][ data_type ] != data :
            
            self.mutex.acquire()
            
            try:
                self.area_tables[ area_id ][ data_type ] = data
                self.ext_communicator.send( data )
                
            except Exception as e:
                self.logger.error("Error while processing data! {}".format( e ) )
                
            finally : 
                self.mutex.release()
                
    def __str__( self ):            
        
        table_str = ""
        
        for sensor_id in self.areas_table.keys():
            
            table_str += "{} data table\n".format( sensor_id )
            
            for data_type in self.areas_table[ sensor_id ].keys() :
                
                table_str += "{} : {}\n".format( data_type, self.areas_table[ sensor_id ][ data_type ] )
                
            table_str += "\n"
            
            
            
            
            
            
            
            
            
            
            
            
            