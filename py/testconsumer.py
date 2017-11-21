'''
Created on Oct 30, 2017

@author: matti
'''

import bclab
import logging
import time

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info('running')
    consumer= bclab.Component(logging, 'localhost', 1883, "test_consumer" )
    consumer.subscribe_data(bclab.TOPIC_DATA)
    consumer.subscribe_analysis('test_producer/analysis')
    while True:
        #producer.produce()
        time.sleep(0.5)
    
