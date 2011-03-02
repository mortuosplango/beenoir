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


function sendNewCode (image, send) {

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


function pingServer() {
    $.ajax({
        url: '/ping?id=' + ID,
        type: 'POST',
        timeout: 1000,
        error: function(){
            // TODO: error message?
        },
        success: function(json){
            // Who cares? This was one-way.
        }
    });
    
    window.setTimeout("pingServer()", 1500);
}
