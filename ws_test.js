// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:8080');

// Connection opened
socket.addEventListener('open', function (event) {
    socket.send('Hello Server!');
});

// Listen for messages
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});


var ws = new WebSocket("ws://localhost:8000/ws");
ws.onopen = function() {
    console.log("Sending websocket data");
    ws.send(JSON.stringify({username:'samson', password: 'BmPW0W8s1^@l'}));
};

ws.send(JSON.stringify({start:'background_sync'}));