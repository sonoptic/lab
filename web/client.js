var img = document.getElementById("liveImg");

var voltText = document.getElementById("volt");
var ampText = document.getElementById("amp");
var percText = document.getElementById("perc");
var cpuText = document.getElementById("cpu");
var freqText = document.getElementById("freq");
var tempText = document.getElementById("temp");
var memText = document.getElementById("mem");
var fpsText = document.getElementById("fps");

var target_fps = 60;

var request_start_time = performance.now();
var start_time = performance.now();
var time = 0;
var request_time = 0;
var time_smoothing = 0.9; // larger=more smoothing
var request_time_smoothing = 0.2; // larger=more smoothing
var target_time = 1000 / target_fps;

var wsProtocol = (location.protocol === "https:") ? "wss://" : "ws://";
const url ='http://192.168.1.105:8000/status';

var path = location.pathname;
if(path.endsWith("index.html"))
{
    path = path.substring(0, path.length - "index.html".length);
}
if(!path.endsWith("/")) {
    path = path + "/";
}
var ws = new WebSocket(wsProtocol + location.host + path + "websocket");
ws.binaryType = 'arraybuffer';

function requestImage() {
    request_start_time = performance.now();
    ws.send('more');
}

ws.onopen = function() {
    console.log("connection was established");
    start_time = performance.now();
    requestImage();
    get_status();
};

ws.onmessage = function(evt) {


    var arrayBuffer = evt.data;
    var blob  = new Blob([new Uint8Array(arrayBuffer)], {type: "image/jpeg"});
    img.src = window.URL.createObjectURL(blob);

    var end_time = performance.now();
    var current_time = end_time - start_time;
    // smooth with moving average
    time = (time * time_smoothing) + (current_time * (1.0 - time_smoothing));
    start_time = end_time;
    var fps = Math.round(1000 / time);
    fpsText.textContent = "Stream FPS: " + fps;

    var current_request_time = performance.now() - request_start_time;
    // smooth with moving average
    request_time = (request_time * request_time_smoothing) + (current_request_time * (1.0 - request_time_smoothing));
    var timeout = Math.max(0, target_time - request_time);



    setTimeout(requestImage, timeout);
};


function get_status(){
    $.ajax(url, {
        success: function(data) {
            voltText.textContent = data["voltage"] + "V";
            ampText.textContent =  data["current"] + "A";
            percText.textContent = data["percentage"] + "% ";
            cpuText.textContent =  data["cpu_usage"] + "%";
            freqText.textContent = data["cpu_freq"] + "Mhz";
            tempText.textContent = data["temp"];
            memText.textContent = data["memory"] + "MB";

            setTimeout(get_status, 400);
        },
        error: function() {
         console.log("error bro");
        }
    })
}