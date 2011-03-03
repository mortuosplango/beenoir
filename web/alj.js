// prepare opcode-image-lookup tables
var topOpcodes = Array(8);
var opcodes = Array(8);

for(var i = 0; i < 8; i++) {
    opcodes[i] = Array(10);
}


var failedTransmissionCount = 0;

function ajaxErrorFunction() {
    failedTransmissionCount += 1;
    
    if(failedTransmissionCount > 3) {
        alert("Netzwerproblem!");
    }
}


function ajaxSuccessFunction(ret) {
    failedTransmissionCount = 0;
    
    if(ret == "fail") {
        self.location.href = "/fail";
    }
}

function changeCode(pos, opcode, send) {

    send = typeof(send) != 'undefined' ? send : true;
    
    code[pos] = opcode;
    
    var currentImage = opcodes[pos][opcode];
    currentImage.src = "/static/opclick.png";
    
    for (var i = 0; i < 10; i++) {
        if(i != opcode) {
            opcodes[pos][i].src = "/static/opcodes_1" + (i) + ".png";
        }
    }
    // first line:
    topOpcodes[pos].src = "/static/opcodes_" + opcode + ".png";
    
    setTimeout(function () {
        currentImage.src = "/static/opcodes_" + opcode + ".png";
    },250);
    
    if(send == true)
    {
        sendCodes();
    }
}

function resetCodes()
{
    code = [0,0,0,0,0,0,0,0];

    for(var i = 0; i < 8; i++){
        changeCode(i, 0, false);
    }
    
    sendCodes();
}

function sendCodes()
{
 $.ajax({
        url: '/code?id=' + ID,
        type: 'POST',
        dataType: 'json',
        data: $.toJSON({"code": code}),
        timeout: 1000,
        error: ajaxErrorFunction,
        success: ajaxSuccessFunction
    });
}


function pingServer() {
    $.ajax({
        url: '/ping?id=' + ID,
        type: 'POST',
        timeout: 1000,
        error: ajaxErrorFunction,
        success: ajaxSuccessFunction
    });
    
    window.setTimeout("pingServer()", 1500);
}

function populateOpcodeTable() {
    for(var i = 0; i < 8; i++) {
        topOpcodes[i] = document.getElementById(i + "_x");
        for(var e = 0; e < 10; e++) {
            opcodes[i][e] = document.getElementById(i + "_" + e);
        }
    }
}