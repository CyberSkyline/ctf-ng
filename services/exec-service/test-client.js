const ws = require('ws');

const socket = new ws.WebSocket('http://127.0.0.1/ng/admin/container/exec', { headers : { 'container-id' : '1' } });
// const socket = new ws.WebSocket('http://127.0.0.1:8099/', { headers : { 'docker-id' : '609e443e75b1' } });

const socketStream = ws.createWebSocketStream(socket);

socketStream.pipe(process.stdout);
process.stdin.pipe(socketStream);
