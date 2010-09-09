function sendMsg (address, data, types) {
    data = $.toJSON({"address":address, 
		     "data": data, 
		     "types": types});
    //debug("create data = " + data);
    $.ajax({
	url: '/command',
	type: 'POST',
	dataType: 'json',
	data: data,
	timeout: 1000,
	error: function(){
	    // TODO: error message?
	},
	success: function(json){
	    // Who cares? This was one-way.
	}
    });
}
function sendNewCode (ID) {
    sendMsg("/alj/code", 
	    [ID, 
	     document.code.code0.selectedIndex,
	     document.code.code1.selectedIndex,
	     document.code.code2.selectedIndex,
	     document.code.code3.selectedIndex,
	     document.code.code4.selectedIndex,
	     document.code.code5.selectedIndex,
	     document.code.code6.selectedIndex,
	     document.code.code7.selectedIndex], 
	    "siiiiiiii");
}

function getValue () {
    var value = "";
    if (document.cookie) {
	var valueStart = document.cookie.indexOf("=") + 1;
	var valueEnd = document.cookie.indexOf(";");
	if (valueEnd == -1)
	    valueEnd = document.cookie.length;
	value = document.cookie.substring(valueStart, valueEnd);
    }
    return value;
}

function setValue (name, value, expiration) {
    var now = new Date();
    var expires = new Date(now.getTime() + expiration);
    document.cookie = name + "=" + value + "; expires=" + expires.toGMTString() + ";";
}

function getID () {
    var expiration = 1000 * 60 * 60 * 24; // 24 hours
    var ID = getValue();
    if (ID == "") {
	var now = new Date();
	ID = now.getTime();
	ID = new String(ID);
	ID = ID + "id"
	setValue("ID", ID , expiration);
	//document.code.name.value = ID.slice(ID.length - 13, ID.length - 1);
    }
    return ID;
}

function pingServer() {
    sendMsg("/alj/ping", [ID], "s");
    window.setTimeout("pingServer()", 1500);
}

function changeName (ID) {
    sendMsg("/alj/name", [ID,document.code.name.value],"ss");
}