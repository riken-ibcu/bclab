'''
Created on 2017/09/12

@author: admin
'''

import paho.mqtt.client as mqtt
import json
import datetime
import traceback
import socket

TOPIC_STATUS = "bcbus/status"
TOPIC_COMMAND = "bcbus/command"
TOPIC_DATA = "bcbus/data"
TOPIC_EVENT = "bcbus/event"
TOPIC_ANALYSIS = "bcbus/analysis"

STATUS_DISCONNECTED = "STATE_DISCONNECTED"
STATUS_CONNECTED = "STATE_CONNECTED"
STATUS_ARMED = "STATE_ARMED"
STATUS_TRIGGERED = "STATE_TRIGGERED"

COMMAND_CONNECT = "COMMAND_CONNECT"
COMMAND_DISCONNECT = "COMMAND_DISCONNECT"
COMMAND_ARM = "COMMAND_ARM"
COMMAND_DISARM = "COMMAND_DISARM"
COMMAND_TRIGGER_ON = "COMMAND_TRIGGER_ON"
COMMAND_TRIGGER_OFF = "COMMAND_TRIGGER_OFF"
COMMAND_STATUS = "COMMAND_STATUS"
COMMAND_MARK = "COMMAND_MARK"

QOS = 1



class DataChannel():
    def __init__(self, name, offset, range_min, range_max, signal_type):
        self.name = name
        self.offset = offset
        self.range_min = range_min
        self.range_max = range_max
        self.signal_type = signal_type
                 
class Component:
    _status = STATUS_DISCONNECTED
    _status_message = ''
    
    state_transfers = {
        STATUS_DISCONNECTED: {COMMAND_CONNECT: STATUS_CONNECTED },
        STATUS_CONNECTED: {COMMAND_DISCONNECT: STATUS_DISCONNECTED, COMMAND_ARM: STATUS_ARMED},
        STATUS_ARMED: {COMMAND_TRIGGER_ON: STATUS_TRIGGERED, COMMAND_DISARM: STATUS_CONNECTED},
        STATUS_TRIGGERED: {COMMAND_TRIGGER_OFF: STATUS_CONNECTED}
    }

    def __init__(self, logger, broker_address, broker_port, client_id):
        logger.info('"%s" connecting to: %s:%s' % (client_id, broker_address , broker_port))
        self.log = logger
        self.client_id = client_id
       
        self.mq = mqtt.Client(client_id, clean_session=True, userdata=self, protocol=mqtt.MQTTv31)
 
        self.mq.on_message = self._on_message
        self.mq.on_log = self._on_log
        self.mq.on_connect = self._on_connect

        self.mq.connect(broker_address, int(broker_port), keepalive=60)

        self.mq.subscribe(TOPIC_COMMAND, qos=QOS)
        self.mq.subscribe(TOPIC_EVENT, qos=QOS)
   
        self.notify_status()
        self.mq.loop_start()
    
    def _on_connect(self, mq, connector, flags, rc):
        if rc:
            connector.log.error("Connector returned " + mqtt.error_string(rc))
        else:
            connector.log.info("Connected to Broker")
            connector.notify_status()
            
    def _on_message(self, mq,  connector, msg):
        try:
            msg.payload = msg.payload.decode('utf-8')
            payload = json.loads(msg.payload)
    
            if msg.topic == TOPIC_COMMAND:
                connector.on_command(payload)
            elif msg.topic == TOPIC_DATA:
                if 'data' in payload:
                    if connector.get_status() in [STATUS_ARMED, STATUS_TRIGGERED]:
                        connector.on_data_stream(msg.topic, payload)
                else:
                    connector.on_data_init(msg.topic, payload)
            elif 'analysis_id' in payload:
                connector.on_analysis(msg.topic, payload)
            elif msg.topic == TOPIC_EVENT:
                connector.on_event(msg.topic, payload)
            elif msg.topic == TOPIC_STATUS:
                connector.on_status(payload)
    
        except:
            err_msg = traceback.format_exc()
            connector.log.error(err_msg)
            connector._status_message = err_msg
            connector.notify_status()


    def _on_log(self, mq, connector, level, string):
        if level == mqtt.MQTT_LOG_ERR:
            connector.log.error(string)
        elif level == mqtt.MQTT_LOG_WARNING:
            connector.log.warning(string)
    
        
    def get_status(self):
        return self._status

    def on_command(self, msg):
        command = msg['command']        

        self.log.info("COMMAND: " + command + " " + str(msg))
        valid_transfers = self.state_transfers[self._status]
        if command in valid_transfers:
            if command == COMMAND_CONNECT:
                self.on_connect(msg)
            elif command == COMMAND_ARM:
                self.on_arm(msg)
            elif command == COMMAND_TRIGGER_ON:
                self.on_trigger_on(msg)
            elif command == COMMAND_TRIGGER_OFF:
                self.on_trigger_off(msg)
            elif command == COMMAND_DISARM:
                self.on_disarm(msg)
            elif command == COMMAND_DISCONNECT:
                self.on_disconnect(msg)
                
            new_status = valid_transfers[command]
            self._status = new_status
            self.log.info( "status changed to " + new_status)
            self.notify_status()            
        elif command == COMMAND_STATUS:
            self.on_status(msg)
            self.notify_status()
                    
    def notify_status(self):
        payload = {"status": self._status,
                   "client_id": self.client_id,
                   "time_utc": datetime.datetime.utcnow().isoformat(),
                   "clock_id": socket.gethostname(),
                   "message": self._status_message}
        (result, _) = self.mq.publish(TOPIC_STATUS, json.dumps(payload), qos=QOS)
        if result:
            self.log.error(mqtt.error_string(result))
            
            
    def subscribe_data(self, topic_id):
        (result, _) = self.mq.subscribe(topic_id, qos=QOS)
        if result:
            self.log.error(self.mq.error_string(result))
        
    def subscribe_analysis(self, analysis_id):
        (result, _) = self.mq.subscribe(analysis_id, qos=QOS)
        if result:
            self.log.error(self.mq.error_string(result))

    def post_analysis(self, analysis_id, **kwargs):
        kwargs['analysis_id'] = analysis_id
        self.log.info('post analysis')
        self.log.info(kwargs)
        (result, _) = self.mq.publish(analysis_id, json.dumps(kwargs), qos=QOS)
        if result:
            self.log.error(self.mq.error_string(result))

    def post_event(self, event_id, **kwargs):
        kwargs['event_id'] = event_id
        self.log.info('post event')
        self.log.info(kwargs)
        (result, _) = self.mq.publish(TOPIC_EVENT, json.dumps(kwargs), qos=QOS)     
        if result:
            self.log.error(self.mq.error_string(result))
  

    def __del__(self):
        self.mq.loop_stop()
        self.mq.disconnect()
        self.mq = None
        self.listeners = []
        
    def on_data_init(self, channel_id, msg):
        pass
    
    def on_data_stream(self, channel_id, msg):
        pass
    
    def on_analysis(self, analysis_id, msg):
        pass
        
    def on_event(self, event_id, msg):
        pass
    
    def on_connect(self, attr):
        pass
    
    def on_arm(self, attr):
        pass

    def on_trigger_on(self, attr):
        pass
    
    def on_trigger_off(self, attr):
        pass

    def on_disarm(self, attr):
        pass
    
    def on_disconnect(self, attr):
        pass       
    
    def on_status(self, attr):
        pass
    
class Producer(Component):
    def __init__(self, logger, broker_address, broker_port, client_id):
        super(Producer, self).__init__(logger, broker_address, broker_port, client_id)
        
        self.stream_id = ''
        self.stream_initializer = ""
        
    def on_status(self, attr):
        if  self.stream_initializer: 
            self._send_stream_initializer()
            
    def initialize_data(self, sampling_rate, data_stride, channels):
        self.stream_id = str(datetime.datetime.now())
        ch_out = []
        for ch in channels:
            ch_out.append(ch.__dict__)
        self.log.info(json.dumps(ch_out))

        payload = {"client_id": self.client_id,
                   "time_utc":datetime.datetime.utcnow().isoformat(), 
                   "clock_id": socket.gethostname(),
                   "sampling_rate": sampling_rate, 
                   "data_stride": data_stride, 
                   "channels": ch_out, 
                   "stream_id": self.stream_id}
        
        self.stream_initializer = json.dumps(payload)
        self._send_stream_initializer()

    def _send_stream_initializer(self):
        (result, _mid) = self.mq.publish(TOPIC_DATA, self.stream_initializer, qos=QOS)
        if result:
            self.log.error(self.mq.error_string(result))


    def stream_data(self, data_string, first_scan, scan_count):
        payload = {"client_id": self.client_id, 
                   "first_scan": first_scan, 
                   "scan_count": scan_count, 
                   "data": data_string, 
                   "stream_id": self.stream_id}
        (result, _mid) = self.mq.publish(TOPIC_DATA, json.dumps(payload), qos=QOS)
        if result:
            self.log.error(self.mq.error_string(result))

class Controller(Component):   
    def __init__(self, logger, broker_address, broker_port, client_id):
        super(Controller, self).__init__(logger, broker_address, broker_port, client_id)
        self.mq.subscribe(TOPIC_STATUS, qos=QOS)
    
    def on_status(self, attr):
        pass
         
    def command(self, command, **kwargs):
        kwargs['command'] = command
        self.mq.publish(TOPIC_COMMAND, json.dumps(kwargs), qos=QOS)
    
    def connect(self):
        self.command(COMMAND_CONNECT)
        
    def arm(self, dst_path=''):
        self.command(COMMAND_ARM, dst_path=dst_path)
        
    def trigger_on(self):
        self.command(COMMAND_TRIGGER_ON)
        
    def trigger_off(self):
        self.command(COMMAND_TRIGGER_OFF)
    
    def disarm(self):    
        self.command(COMMAND_DISARM)
    
    def disconnect(self):
        self.command(COMMAND_DISCONNECT)
