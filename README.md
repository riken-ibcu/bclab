# BCLAB
*integration platform for neuro-rehabilitation*


## Basic test kit

These tools introduce the core functionality of the platform.  Run producer and consumer each in its own console. Use either python controller or web controller to control the state of the system.

### python
- testcontroller.py: a supervisory application
- testproducer.py: a data stream source with analysis
- testconsumer.py: a data stream sink with printing

### web
- testcontroller.html: an alternative supervisory application

## Messaging performance evaluation

Application to measure a message roundtrip time between two clients conditioned with Quality of Service.

- roundtripa.py qos: source for messages
- roundtripb.py: echo

## Streaming performance evaluation

Application to measure streaming performance, measures time difference between packets in the stream. Use streamcontroller.html or testcontroller.py to control the application state.
### python
- streama.py qos rows_to_send: stream source
- streamb.py qos filename: stream sink
### web
- streamcontroller.html