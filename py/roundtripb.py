'''
Created on Apr 10, 2018

@author: matti
'''

import bclab
import logging
import time
import sys

class ClientB(bclab.Component):
    def __init__(self, logger, broker_address, broker_port, client_id, qos):
        super(ClientB, self).__init__(logger, broker_address, broker_port, client_id, qos)
        self.subscribe_analysis('roundtrip')

    def on_analysis(self, analysis_id, msg):
        self.post_analysis('echo', time=msg['time'])

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    qos = int(sys.argv[1]) if len(sys.argv)>1 else 1
    with  ClientB(logging, 'localhost', 1883, "clientb", qos ) as client:
        var = input("Hit <ENTER> to stop!\n")
    
