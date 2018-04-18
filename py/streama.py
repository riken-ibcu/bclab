'''
Created on Oct 30, 2017

@author: matti
'''

import bclab
import logging
import time
import numpy as np
import base64
import threading
import sys

class StreamA(bclab.Producer, threading.Thread):
    def __init__(self, logger, broker_address, broker_port, client_id, n_channels=50, rows_per_message=200, qos=1):
        bclab.Producer.__init__(self,logger, broker_address, broker_port, client_id, qos=qos)
        threading.Thread.__init__(self)
        self.total_rows_sent = 0
        self.n_channels=n_channels
        self.fq_adj= np.random.randint(50,300,n_channels)
        self.rows_per_message=rows_per_message
        self.daemon=True
        self.start()
    
    def on_arm(self, attr):
        chs =[]
        for i in range(self.n_channels):
            ch = bclab.DataChannel("channel %i" % i, i, -1, 1, "stream1")
            chs.append(ch)
        self.initialize_data(2000, len(chs), chs)
    
    def run(self):
        nxt=  time.perf_counter()+1
        iv = 0.1
        while(True):
            status = self.get_status()
    
            if status in [bclab.STATUS_ARMED, bclab.STATUS_TRIGGERED]:
                bbuf = np.zeros((self.rows_per_message, self.n_channels), np.float32)
                for i in range(0,self.n_channels):
                    c=0.8*np.sin(np.arange(self.total_rows_sent,self.total_rows_sent+self.rows_per_message)/self.fq_adj[i])+np.random.rand(self.rows_per_message)*0.2
                    bbuf[:,i]=c
                s = base64.b64encode(bbuf).decode("utf-8")
                self.stream_data(s, self.total_rows_sent, self.rows_per_message)
                self.total_rows_sent += self.rows_per_message            
            now = time.perf_counter()

            d = nxt-now
            nxt += iv
            if (d>0):
                time.sleep(d)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info('running')
    
    qos = int(sys.argv[1]) if len(sys.argv) > 1 else 1   
    rows_to_send = int(sys.argv[2]) if len(sys.argv) > 2 else 20000   
    with StreamA(logging, 'localhost', 1883, "streama", 50, 200, qos ) as producer:
        while(producer.total_rows_sent < rows_to_send):
           time.sleep(0.5)
   
    logging.info('done')
   