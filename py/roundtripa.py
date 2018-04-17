'''
Created on Apr 10, 2018

@author: matti
'''

import bclab
import logging
import time
import numpy as np
import sys

class ClientA(bclab.Component):
    def __init__(self, logger, broker_address, broker_port, client_id, qos):
        super(ClientA, self).__init__(logger, broker_address, broker_port, client_id, qos)
        self.subscribe_analysis('echo')
        self.res={}

    def on_analysis(self, analysis_id, msg):
        if (analysis_id=='echo'):
            self.log.info(msg)
            t='%20.10f' % time.perf_counter()
            
            k=msg['time']
            if k in self.res and self.res[k] is None:
                self.res[k] = t
        else:
            print(analysis_id)
        
    def run(self, interval, n):
        for i in range(n):
            t = '%20.10f' % time.perf_counter()
            self.res[t]=None
            self.post_analysis('roundtrip', time=t)
            time.sleep(interval)
            

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    qos = int(sys.argv[1]) if len(sys.argv)>1 else 1
    filename = sys.argv[2] if len(sys.argv)>2 else None
         
    client= ClientA(logging, 'localhost', 1883, "clienta", qos )
    
    client.run(0.1, 1000)
    time.sleep(1)
    print('done')
    d = []
    missed=[]
    for k in client.res.keys():
        e = client.res[k]
        if e is None:
            missed.append(k)
        else:
            d.append(float(e)-float(k))
    print('missed', len(missed), missed)
    print('mean', np.mean(d))
    print('sd', np.std(d))

    if filename:
        thefile = open(filename, 'w')
        for item in d:
            thefile.write("%f\n" % item)            
        thefile.close()