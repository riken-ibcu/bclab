var _graphs=[]

function Signal(name, stride, offset, topValue, bottomValue) {
	this.name = name;
	this.stride = stride;
	this.offset = offset;
	this.topValue = topValue;
	this.bottomValue = bottomValue;
	this.row = 0;
	this.col = 0;
	this.offsetY = 0;
	this.gainY = 0;
	this.offsetX = 0;
};

function canvasClicked(event)  //element that is used to draw graphics
{
  var x = event.x;
  var y = event.y;

  var sender = (event && event.target) || (window.event && window.event.srcElement);

  x -= sender.offsetLeft;
  y -= sender.offsetTop;

  var graph = null
   _graphs.forEach(function(g) {
			if (g.canvas == sender) {
			    graph = g
			}
		})
	graph.isZoomed = !graph.isZoomed;


    graph.context.clearRect(0,0, graph.canvas.width, graph.canvas.height);
    graph.zoomedIdx = Math.floor(y/(graph.canvas.height/(graph.signals.length)))

    signal = graph.signals[graph.zoomedIdx]

    var x0=signal.topValue;
    var x1=signal.bottomValue;
    var y0= 0;
    var y1= graph.canvas.height;

    graph.zoomedGain = (y1-y0)/(x1-x0);
    graph.zoomedOffset = y0-x0*graph.zoomedGain;

}



function Graph(canvas, client, widthSeconds) {
    this.client = client;
	this.canvas = canvas;
	this.context = this.canvas.getContext("2d");
	this.widthSeconds = widthSeconds;
	canvas.addEventListener("click", canvasClicked, false)
	_graphs.push(this)
	this.isZoomed = false;
	this.zoomedIdx = 0;
	this.zoomedGain = 1;
	this.zoomedOffset = 0;

};

Graph.prototype.calibrate = function(streamId, signals, rows, cols, samplingRateHz) {
	this.canvas.width=this.canvas.parentNode.clientWidth
	this.canvas.height=this.canvas.parentNode.clientHeight
	
	this.streamId = streamId;
	this.samplingRateHz = samplingRateHz;
	this.samplesOnPlot = this.samplingRateHz * this.widthSeconds; 
	this.samplesPerLine = this.samplesOnPlot/(this.canvas.width)*cols;
	this.rows = rows;
	this.cols = cols;
	
	this.signals = signals;
	
	var si;
	for (si = 0; si < signals.length; ++si) {
	    signal = signals[si];
	    signal.col = Math.floor(si/rows);
	    signal.row = Math.floor(si%rows);
	    
	    var x1=signal.topValue;
	    var x0=signal.bottomValue;
	    var y0= this.canvas.height/this.rows*signal.row;
	    var y1= this.canvas.height/this.rows*(signal.row+1);
	    
	    signal.gainY = (y1-y0)/(x1-x0);
	    signal.offsetY = y0-x0*signal.gainY;

		signal.offsetX = this.canvas.width*(signal.col/this.cols);
	}
};

Graph.prototype.draw = function(streamId, data, firstRow, numberOfRows) {
	if ('streamId' in this && this.streamId == streamId) {
		var si;
		
		this.context.font="30px Arial";
   		if (this.isZoomed) {
            this._clear(this.signals[this.zoomedIdx], firstRow, numberOfRows);
            this.context.fillText(this.signals[this.zoomedIdx].name, 0, 0.25*this.canvas.height);
         } else {
            for (si = 0; si < this.signals.length; ++si) {
                this._clear(this.signals[si], firstRow, numberOfRows);
                this.context.fillText(this.signals[si].name, this.signals[si].offsetX, (this.signals[si].row+0.25)*(this.canvas.height/this.rows));
            }
        }

		this.context.beginPath();
		if (this.isZoomed) {
                this._drawSignal(this.signals[this.zoomedIdx], data, firstRow, numberOfRows);
		} else {
            for (si = 0; si < this.signals.length; ++si) {
                this._drawSignal(this.signals[si], data, firstRow, numberOfRows);
            }
        }
		this.context.stroke();
	}

};

Graph.prototype._clear = function(signal, firstRow, numberOfRows) {
	var x0=(firstRow%this.samplesOnPlot)/this.samplesPerLine;
	var x1=((firstRow+numberOfRows)%this.samplesOnPlot)/this.samplesPerLine;
	
	var height = this.canvas.height/this.rows;
	var top = signal.row*height;

	if (this.isZoomed) {
        height = this.canvas.height;
        top = 0;
	}
	
	if (x1>x0) {
		this.context.clearRect(signal.offsetX + x0+2, top, (x1-x0+1), height);
	} else {
		this.context.clearRect(signal.offsetX, top, x1, height);
		this.context.clearRect(signal.offsetX + x0, top, (this.canvas.width/this.cols)-x0, height);
	}
};

Graph.prototype._drawSignal = function(signal, data, firstRow, numberOfRows) {
	var context = this.context;
	
	var dataIdx= signal.offset;
	var mn = 0;
	var mx = 0;
	var lineBreak = firstRow;
	var firstLine = true;

	var ox = signal.offsetX;
	var gy = signal.gainY;
	var oy = signal.offsetY;

	if (this.isZoomed) {
	    ox = 0;
	    gy = this.zoomedGain;
	    oy = this.zoomedOffset;
	}

	for (var row = 0; row<numberOfRows; row++) {
		var dataPoint = data[dataIdx];
		dataIdx += signal.stride;
		if (firstLine) {
			mn=dataPoint;
			mx=dataPoint;
			lineBreak += this.samplesPerLine;
			firstLine = false;
		} else {
			if (dataPoint < mn) {
				mn = dataPoint;
			}
			if (dataPoint > mx) {
				mx = dataPoint;
			}
		}	
		if (row + firstRow > lineBreak || row == numberOfRows-1) {
			var x=(lineBreak%this.samplesOnPlot)/this.samplesPerLine;
			context.moveTo(ox+x,(mn*gy)+oy+0);
			context.lineTo(ox+x,(mx*gy)+oy-1);
			firstLine = true;
		}
	};
};







