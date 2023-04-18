const WebSocket = require('ws');

// Create a WebSocket server
const wss = new WebSocket.Server({ port: 8080 });
console.log(wss.address())

// Keep track of connected clients
const clients = new Set();

// Handle incoming WebSocket connections
wss.on('connection', (ws) => {
    console.log('Client connected');
    clients.add(ws);

    // Handle incoming signaling messages from the Python server or the React website
    ws.on('message', (message) => {
        console.log('Received message:');

        // Broadcast the signaling message to all other clients
        clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });
    });

    // Handle WebSocket disconnections
    ws.on('close', () => {
        console.log('Client disconnected');
        clients.delete(ws);
    });
});
