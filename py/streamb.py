'''
Created on Apr 13, 2018

@author: matti
'''

import bclab
import logging
import time
import sys

class StreamB(bclab.Producer):
    def __init__(self, logger, broker_address, broker_port, client_id, n_channels=50, rows_per_message=200, qos=1):
        bclab.Producer.__init__(self,logger, broker_address, broker_port, client_id, qos=qos)
        self.acc = [0]*1500
        self.idx = 0
        self.subscribe_data('streama')

 
    def on_data_stream(self, channel_id, msg):
        if channel_id=='streama' and self.idx<1500:
        	self.acc[self.idx]=time.perf_counter()
        	self.idx += 1
    
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
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    with StreamB(logging, 'localhost', 1883, "streamb", qos ) as consumer:
        var = input("Hit <ENTER> to stop!\n")
        
        if filename:
            thefile = open(filename, 'w')
            for item in consumer.acc:
                thefile.write("%f\n" % item)            
            thefile.close()
    logging.info('done')

	    
