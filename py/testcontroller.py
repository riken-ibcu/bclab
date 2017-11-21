'''
Created on Oct 30, 2017

@author: matti
'''

import bclab
import logging

class TestController(bclab.Controller):
    def on_status(self, attr):
        print('STATUS REPORT')
        print(attr)

if __name__ == '__main__':
    print('test controller')
    print('---------------')
    
    logging.getLogger().setLevel(logging.INFO)
    logging.info('running')
    controller= TestController(logging, 'localhost', 1883, "test_controller" )
 
    command_map= {'1':controller.connect, 
                  '2':controller.arm, 
                  '3':controller.trigger_on,
                  '4':controller.trigger_off,
                  '5':controller.disarm,
                  '6':controller.disconnect}
     
    resp=''
    while resp != '0':
        resp=input('1: connect, 2: arm, 3: trigger on, 4: trigger off, 5:disarm, 6: disconnect or 0: exit?')
        if (resp in command_map):
            command_map[resp]()
        
    logging.info('done')
    


    