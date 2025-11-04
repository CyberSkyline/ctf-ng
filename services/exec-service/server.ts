const Docker = require('dockerode');
const ws = require('ws');
const fs = require('fs');

const wss = new ws.WebSocketServer({ port : 8099, host : '0.0.0.0' });

interface DockerHeaderRequest extends Request {
  headers : Headers & {
    'docker-id' : string,
  }
}

wss.on('connection', (socket: WebSocket, request: DockerHeaderRequest) => {
  const { 'docker-id' : dockerId } = request.headers;

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
      Cmd : [ '/bin/bash' ],
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
  })();
});
