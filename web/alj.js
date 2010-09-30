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


function sendNewCode (ID, image, send) {

  	send = typeof(send) != 'undefined' ? send : true;

    var column = Math.floor(image/10) * 11;
    var opcode = image%10;
    var currentImage = window.document.images[opcode + 1 + column];
    
    currentImage.src = "opclick.png";
    
    for (var i = 0; i < 10; i++) {
        if(i != opcode) {
            window.document.images[column + (i+1)].src = "opcodes_1" + (i) + ".png";
        }
    }
    // first line:
    window.document.images[column].src = "opcodes_" + opcode + ".png";

    code[Math.floor(image/10)] = image%10;
    
    setTimeout(function () {currentImage.src = "opcodes_" + opcode + ".png";},250);
    
    if(send == true)
    {
		sendCodes();
	}
}

function resetCodes()
{
	code = [0,0,0,0,0,0,0,0];

	for(var i = 0; i < 8; i++){
	    sendNewCode(null, i*10, false);
	}
	
	sendCodes();
}

function sendCodes()
{
    sendMsg("/alj/code", 
	        [ID, playerNo, code[0], code[1], code[2], code[3], code[4], 
	         code[5], code[6], code[7]], 
	        "siiiiiiiii");
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
    var expiration = 1000 * 30; // 30 seconds
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
    sendMsg("/alj/ping", [ID, playerNo], "si");
    window.setTimeout("pingServer()", 1500);
}

function getPlayer() {
    sendMsg("/alj/getplayer", [ID], "s");
}

function changeName (ID) {
    sendMsg("/alj/name", [ID,document.code.name.value],"ss");
}