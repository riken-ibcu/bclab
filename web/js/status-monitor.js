function toHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function nowToString() {
    return dateToString(new Date())
}

function dateToString(d) {
    var ds = "" + d.getSeconds();
    if (ds.length<2) {
        ds = "0" + ds;
    }
    ds = d.getMinutes() + ":" + ds;
    if (ds.length<5) {
        ds = "0" + ds;
    }
    ds = d.getHours() + ":" + ds;
    if (ds.length<8) {
        ds = "0" + ds;
    }
    return ds
}

function StatusMonitor(htmlTable) {
    this.table = htmlTable;

    var header = this.table.createTHead();
    var row = header.insertRow(0);
    row.insertCell(0).innerHTML= "<b>Device</b>";
    row.insertCell(1).innerHTML= "<b>Status</b>";
    row.insertCell(2).innerHTML= "<b>Time</b>";
}

StatusMonitor.prototype.update = function(clientStatus) {
	for (var i = 0, row; row = this.table.rows[i]; i++) {
		if (row.cells[0].innerHTML == clientStatus.client_id) {
			break;
			};
	};

	if (typeof row == 'undefined') {
		row = this.table.insertRow(this.table.rows.length);
		row.insertCell(0);
		row.insertCell(1);
		row.insertCell(2);
	}
	
	switch (clientStatus.status) {
	case "STATE_ARMED":
		tx = "Armed";
		cl = "#99ff99";
		break;
	case "STATE_TRIGGERED":
		tx = "Triggered";
		cl = "#ff9999";
		break;
	case "STATE_CONNECTED":
		tx = "Connected";
		cl = "#ffffff";
		break;
	case "STATE_DISCONNECTED":
		tx = "Disconnected";
		cl = "#999999";
	    break;
	default:
		tx= clientStatus.status;
		cl = "#ffffff";
	}
	
	row.cells[0].innerHTML = clientStatus.client_id;
	if ("message" in clientStatus && clientStatus.message.length>0) {
            row.cells[1].innerHTML = '<div><div>' + tx + '</div><div>' + toHtml(clientStatus.message) + '</div></div>';
            row.cells[1].style.backgroundColor = 'yellow';
          } else {
	    row.cells[1].innerHTML = tx;
              row.cells[1].style.backgroundColor = cl;
	}

    var timestamp=""
	if (clientStatus.time_utc) {
		var s = clientStatus.time_utc
		if(s[s.length-1] != 'Z') {
  			s = s+ 'Z'
		}
		var date = new Date(s)
	    timestamp=dateToString(date)
	    var delay = new Date()-new Date(date)
	    timestamp = timestamp + " (" + delay + "ms)"
	} else {
	    timestamp=nowToString()
	}
	row.cells[2].innerHTML = timestamp;
};



