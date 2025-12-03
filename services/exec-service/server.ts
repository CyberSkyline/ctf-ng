const Docker = require('dockerode');
const ws = require('ws');
const fs = require('fs');

const wss = new ws.WebSocketServer({ port : 8099, host : '0.0.0.0' });
const PSK = '';

interface DockerHeaderRequest extends Request {
  headers : Headers & {
    'docker-id' : string,
    'psk' : string,
  }
}

wss.on('connection', (socket: WebSocket, request: DockerHeaderRequest) => {
  const { 'docker-id' : dockerId, psk } = request.headers;

  if (psk !== PSK) {
    socket.send('Unauthorized');
    socket.close();
    return;
  }

  const docker = new Docker({
    host : '127.0.0.1',
    ca : fs.readFileSync('/var/lib/certs/ssl/ca.pem'),
    cert : fs.readFileSync('/var/lib/certs/ssl/cert.pem'),
    key : fs.readFileSync('/var/lib/certs/ssl/key.pem'),
    port : 2376,
  });

  const ctr = docker.getContainer(dockerId);
  (async () => {
    const exec = await ctr.exec({
      Cmd : [ '/bin/sh' ],
      User : 'root',
      Tty : true,
      AttachStdin : true,
      AttachStderr : true,
      AttachStdout : true,
      Env : [ 'HISTFILE=/dev/null' ],
    });
    const execStream = await exec.start({
      hijack : true,
      stdin : true,
      Tty : true,
    });
    const sockStream = ws.createWebSocketStream(socket);
    sockStream.pipe(execStream);
    execStream.pipe(sockStream);

    sockStream.on('error', (err) => {
      console.error('sockStream error:', err);
    });
    execStream.on('error', (err) => {
      console.error('execStream error:', err);
    });

    socket.on('close', async () => {
      // clean up sockets
      execStream.unpipe(sockStream);
      sockStream.unpipe(execStream);
      sockStream.destroy();
      execStream.destroy();
    });
  })();
});
