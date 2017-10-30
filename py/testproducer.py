'''
Created on Oct 30, 2017

@author: matti
'''

import bclab
import logging
import time


class TestProducer(bclab.component):
    
    def on_arm(self):
        self.
    

if __name__ == '__main__':

    
    logging.getLogger().setLevel(logging.INFO)
    logging.info('running')
    producer= bclab.Component(logging, 'localhost', 1883, "test_producer" )
    while True:
 ####       producer.produce('ELEMENT')
        time.sleep(0.5)
    
