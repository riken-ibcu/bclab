'''
Created on Oct 30, 2017

@author: matti
'''

import bclab
import logging
import time

class TestConsumer(bclab.Component):
    def __init__(self, logger, broker_address, broker_port, client_id, qos, stream_source, analysis_id):
       super(TestConsumer, self).__init__( logger, broker_address, broker_port, client_id, qos)
       self.subscribe_data(stream_source)
       self.subscribe_analysis(analysis_id)
       self.stream_source = stream_source
       self.analysis_id = analysis_id
       
    def on_data_init(self, source_client_id, msg):
        if (source_client_id==self.stream_source):
            self.log.info(msg)
        # if (source_client_id== OTHER_CLIENT_ID):
        #    handle here 
    
    def on_data_stream(self, source_client_id, msg):
        if (source_client_id==self.stream_source):
            self.log.info(msg)
        # if (source_client_id== OTHER_CLIENT_ID):
        #    handle here 
    
    def on_analysis(self, analysis_id, msg):
        if (analysis_id == self.analysis_id):
            self.log.info(msg)
        # if (source_analysis_id== OTHER_ANALYSIS_ID):
        #    handle here 
    
    def on_event(self, event):
        self.log.info(event)
        #enter substate(event['event_id'])
    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info('running')
    with TestConsumer(logging, 'localhost', 1883, "test_consumer", 1, 'test_producer', 'test_producer/analysis' ) as consumer:
        var = input("Hit <ENTER> to stop!\n")
    
