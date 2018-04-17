'''
Created on Oct 30, 2017

@author: matti
'''

import bclab
import logging
import time
import numpy as np
import base64

class TestProducer(bclab.Producer):
    def __init__(self, logger, broker_address, broker_port, client_id, n_channels=10, rows_per_message=200):
        super(TestProducer, self).__init__(logger, broker_address, broker_port, client_id, qos=1)
        self.total_rows_sent = 0
        self.is_running = True
        self.n_channels=n_channels
        self.fq_adj= np.random.randint(50,300,n_channels)
        self.rows_per_message=rows_per_message
    
    def on_arm(self, attr):
        chs =[]
        for i in range(self.n_channels):
            ch = bclab.DataChannel("channel %i" % i, i, -1, 1, "emg")
            chs.append(ch)
        self.initialize_data(200, len(chs), chs)

    def produce(self):
        status = self.get_status()

        if status in [bclab.STATUS_ARMED, bclab.STATUS_TRIGGERED]:
            bbuf = np.zeros((self.rows_per_message, self.n_channels), np.float32)
            for i in range(0,self.n_channels):
                c=0.8*np.sin(np.arange(self.total_rows_sent,self.total_rows_sent+self.rows_per_message)/self.fq_adj[i])+np.random.rand(self.rows_per_message)*0.2
                bbuf[:,i]=c
            s = base64.b64encode(bbuf).decode("utf-8")
            self.stream_data(s, self.total_rows_sent, self.rows_per_message)
            self.total_rows_sent += self.rows_per_message

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info('running')
    producer= TestProducer(logging, 'localhost', 1883, "test_producer" )
    loop_iter = 0
    while True:
        producer.produce()
        if producer.get_status() in [bclab.STATUS_ARMED, bclab.STATUS_TRIGGERED] and not loop_iter % 10:
            producer.post_analysis('test_producer/analysis', count=loop_iter)
        time.sleep(1)
        loop_iter += 1
