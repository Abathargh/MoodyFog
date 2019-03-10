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

'''

The following class is a dictionary which can be observed by an object extending the
moodyfog.utility.Observer class and that has a check on __setitem__  that makes it so that
the dictionary isn't touched when

'''

def tmr_decide( input_dict ):

    in1, in2, in3 = list( input_dict.values() )

    if in1 == in2:
        return in1
    if in2 == in3:
        return in2
    if in1 == in3:
        return in1

    return None

class Observer():

    def update( self, updated_data ):
        pass

class Observable():

    def __init__( self ):
        self.observer_list = list()

    def set_observer( self, observer ):
        self.observer_list.append( observer )

    def notify_observers( self, updated_data ):
        for observer in self.observer_list:
            observer.update( updated_data )

class ObservableMultidimensionalDict( dict, Observable ):

    def __init__( self ):
        Observable.__init__(self)
        self.logger = logging.getLogger( __name__ )
        self.mutex = Lock()
        self.repetitions_admitted = False

        self.nested_dict_observer = Observer()

        def update ( updated_value ):
            return self.notify_observers( {list(self.keys())[list(self.values()).index(updated_value)]: updated_value} )

        self.nested_dict_observer.update = update

    def __setitem__( self, key, value ):
        if self.repetitions_admitted or ( ( not self.repetitions_admitted )
                                    and ( key not in self.keys() or ( key in self.keys() and not ( self[ key ] == value ) ) ) ) :

            self.mutex.acquire()

            try:
                if ( isinstance( value, dict ) ):
                    value = ObservableMultidimensionalDict()
                    value.set_observer( self.nested_dict_observer )

                super().__setitem__( key, value )
                self.notify_observers( self )


            finally :
                self.mutex.release()

class ObservableDict( dict, Observable ):

    def __init__( self ):
        Observable.__init__(self)
        self.logger = logging.getLogger( __name__ )
        self.mutex = Lock()
        self.repetitions_admitted = False


    def __setitem__( self, key, value ):
        if self.repetitions_admitted or ( ( not self.repetitions_admitted )
                                    and ( key not in self.keys() or ( key in self.keys() and not ( self[ key ] == value ) ) ) ) :

            self.mutex.acquire()

            try:
                super().__setitem__( key, value )
                self.notify_observers( ( key, value ) )


            finally :
                self.mutex.release()
