
var _busConnector; 

var TOPIC_COMMAND = "bcbus/command";
var TOPIC_STATUS = "bcbus/status";
var TOPIC_EVENT = "bcbus/event";


var COMMAND_CONNECT = "COMMAND_CONNECT";
var COMMAND_ARM = "COMMAND_ARM";
var COMMAND_TRIGGER_ON = "COMMAND_TRIGGER_ON";
var COMMAND_TRIGGER_OFF = "COMMAND_TRIGGER_OFF";
var COMMAND_DISARM = "COMMAND_DISARM";
var COMMAND_DISCONNECT = "COMMAND_DISCONNECT";
var COMMAND_STATUS = "COMMAND_STATUS";

function BcbusConnector(brokerAddr, brokerPort, plots, analysis, statusListeners, eventListeners) {
	this.STATE_DISCONNECTED = "STATE_DISCONNECTED";
	this.STATE_CONNECTED = "STATE_CONNECTED";
	this.STATE_ARMED = "STATE_ARMED";
	this.STATE_TRIGGERED = "STATE_TRIGGERED";

    _busConnector = this;

	var clientName = "bc" + new Date().getTime().toString(10);
    this.client = new Messaging.Client(brokerAddr, brokerPort, clientName);
    console.log("BcbusConnector Client id = " + clientName + "Connecting to " + this.client._getHost() + ":" + this.client._getPort());
    this.client.startTrace();


    this.plots = plots;
    this.analysis = analysis;
    this.statusListeners = statusListeners;
    this.eventListeners = eventListeners;
    this.client.onMessageArrived = this.handleMessage;
    this.client.connect({onSuccess:this.handleConnect, onFailure:this.handleFailure});
    console.log("BcbusConnector created");
}

BcbusConnector.prototype.handleConnect = function() {
	var subs = [TOPIC_STATUS,TOPIC_EVENT]
	for (p in _busConnector.plots) {
		subs.push(_busConnector.plots[p].client)
	}
	for (a in _busConnector.analysis) {
		subs.push(_busConnector.analysis[a].analysis_id)
	}
	for (s in subs) {
		_busConnector.client.subscribe(subs[s])
	}
	_busConnector.status()
	console.log("BcbusConnector connected");
};

BcbusConnector.prototype.handleFailure = function(obj) {
	console.log(obj.errorMessage);
};

BcbusConnector.prototype.handleMessage = function(message) {
	try {
		var payload = JSON.parse(message.payloadString);
		switch (message.destinationName) {
			case TOPIC_STATUS:
				_busConnector.processStatus(message);
				break;
	
			case TOPIC_EVENT:
				_busConnector.processEvents(message)
				break;
		}
		if (payload.hasOwnProperty('stream_id')) {
			_busConnector.processData(payload);
		} else if (payload.hasOwnProperty('analysis_id')) {
			_busConnector.processAnalysis(payload);
		}


	
	} catch (exp) {
		console.log("Exception at message handler:" + exp);
	}
};

BcbusConnector.prototype.processData = function(payload) {
	

	var client = payload.client_id;
	if ('channels' in payload ) {
		var initializer =  payload;
		var signals = [];
		for (var ci = 0; ci < initializer.channels.length; ++ci) {
			var channel = initializer.channels[ci];
			var signal = new Signal(channel.name, initializer.data_stride, channel.offset, channel.range_min, channel.range_max );
			signals.push(signal);
		}

        _busConnector.plots.forEach(function(plot) {
            if ((!plot.client) || (client == plot.client)) {
                plot.calibrate(initializer.stream_id, signals, signals.length, 1, initializer.sampling_rate );
            }
        });
	}
	if ('data' in payload) {
	    var byteArray = base64js.toByteArray(payload.data);

		var data = new Float32Array(byteArray.buffer)
        _busConnector.plots.forEach(function(plot) {
            if ((!plot.client) || (client == plot.client)) {
                plot.draw(payload.stream_id, data, payload.first_scan, payload.scan_count);
            }
        });
	}
};

BcbusConnector.prototype.processAnalysis = function(payload) {

	var client = payload.client_name;

    _busConnector.analysis.forEach(function(ana) {
		try {
			var patt=new RegExp(ana.analysis_name)
				if ( patt.test( payload.name)) {
					payload.analysis.name=payload.name;
					ana.draw(payload.analysis);
				}
		} catch(exp) {
				console.log("Exception at analysis:" + exp);
		}
    });

};

BcbusConnector.prototype.processStatus= function(message) {
	if (typeof _busConnector.statusListeners === 'undefined') {
		return;
	}
	
	var payload = JSON.parse(message.payloadString);
	var client = payload.client_id;

    _busConnector.statusListeners.forEach(function(el) {
    	try {
            el.update(payload);
        } catch(exp) {
        	console.log("Exception at status:" + exp);
		}
    });	
};

BcbusConnector.prototype.processEvents = function(message) {
	if (typeof _busConnector.eventListeners === 'undefined') {
		return;
	}
	var payload = JSON.parse(message.payloadString);
	var client = payload.client_name;

    _busConnector.eventListeners.forEach(function(el) {
 try {
            el.update(payload);
            } catch(exp) {
		console.log("Exception at events:" + exp);

}
    });
};

BcbusConnector.prototype.send = function(cmd) {
	var msg = new Messaging.Message(cmd);
	msg.destinationName = TOPIC_COMMAND;
	_busConnector.client.send(msg);

};

BcbusConnector.prototype.send_event = function(event) {
	var json = JSON.stringify(event);
	var msg = new Messaging.Message(json);
	msg.destinationName = TOPIC_EVENT;
	_busConnector.client.send(msg);
}

BcbusConnector.prototype.connect = function() {
	var cmd = JSON.stringify({command:COMMAND_CONNECT})
	_busConnector.send(cmd);
};

BcbusConnector.prototype.arm = function(dest) {
	var msg = {command: COMMAND_ARM, destination: dest};
	var json = JSON.stringify(msg);
	_busConnector.send(json);
};

BcbusConnector.prototype.triggerOn = function() {
	var cmd = JSON.stringify({command:COMMAND_TRIGGER_ON})
	_busConnector.send(cmd);
};

BcbusConnector.prototype.triggerOff = function() {
	var cmd = JSON.stringify({command:COMMAND_TRIGGER_OFF})
	_busConnector.send(cmd);
};

BcbusConnector.prototype.disarm = function() {
	var cmd = JSON.stringify({command:COMMAND_DISARM})
	_busConnector.send(cmd);
};

BcbusConnector.prototype.disconnect = function() {
	var cmd = JSON.stringify({command:COMMAND_DISCONNECT})
	_busConnector.send(cmd);
};

BcbusConnector.prototype.status = function() {
	var cmd = JSON.stringify({command:COMMAND_STATUS})
	_busConnector.send(cmd);
};


