// prepare opcode-image-lookup tables


var topOpcodes = Array(CODESIZE);
var opcodes = Array(CODESIZE);

for(var i = 0; i < CODESIZE; i++) {
    opcodes[i] = Array(NUMCODES);
}


var failedTransmissionCount = 0;

function ajaxErrorFunction() {
    failedTransmissionCount += 1;
    
    if(failedTransmissionCount > 3) {
        showTimeout();
    }
}


function ajaxSuccessFunction(ret) {
    failedTransmissionCount = 0;
    document.getElementById('timeOut').style.display = 'none';
    
    if(ret == "fail") {
        self.location.href = "/fail";
    }
}

function changeCode(pos, opcode, send) {

    send = typeof(send) != 'undefined' ? send : true;
    
    code[pos] = opcode;
    
    var currentImage = opcodes[pos][opcode];
    currentImage.src = "/static/opclick.png";
    
    for (var i = 0; i < NUMCODES; i++) {
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

function changeTempo(newTempo) {
    
    if(newTempo < 0) {
        newTempo = 0;
    } else if (newTempo >= NUMTEMPOS) {
        newTempo = NUMTEMPOS - 1;
    }
    
    
    for(var i = 0; i < NUMTEMPOS; i++) {
        var cur = document.getElementById('tempo_' + i);
        var className;
        if(i == newTempo) {
            className = "button tempo on";
        } else {
            className = "button tempo off";
        }
        
        if(i == 0) {
            className = className + " first";
        } else if (i == NUMTEMPOS - 1) {
            className = className + " last";
        }
        cur.className = className;
    }
    
    sendTempo(newTempo);
}

function resetCodes()
{
    for(var i = 0; i < CODESIZE; i++){
        changeCode(i, NUMCODES-1, false);
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

function visualHint()
{
 $.ajax({
        url: '/visual_hint?id=' + ID,
        type: 'POST',
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


function sendTempo(newTempo) {
    $.ajax({
        url: '/tempo?id=' + ID,
        type: 'POST',
        timeout: 1000,
        error: ajaxErrorFunction,
        success: ajaxSuccessFunction,
        dataType: 'json',
        data: $.toJSON({"tempo": newTempo})
    });
}

function populateOpcodeTable() {
    for(var i = 0; i < CODESIZE; i++) {
        topOpcodes[i] = document.getElementById(i + "_x");
        for(var e = 0; e < NUMCODES; e++) {
            opcodes[i][e] = document.getElementById(i + "_" + e);
        }
    }
}

function showHelp() {
    document.getElementById('help').style.display = 'block';
    document.getElementById('about').style.display = 'none';
}

function showAbout() {
    document.getElementById('help').style.display = 'none';
    document.getElementById('about').style.display = 'block';
}

function showGame() {
    document.getElementById('help').style.display = 'none';
    document.getElementById('about').style.display = 'none';
}

function showTimeout() {
    showGame();
    document.getElementById('timeOut').style.display = 'block';
}