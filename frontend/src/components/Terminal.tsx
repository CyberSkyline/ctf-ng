import { WebglAddon } from '@xterm/addon-webgl';
import { Terminal as XTerm } from '@xterm/xterm';
import '@xterm/xterm/css/xterm.css';
import { useCallback, useEffect, useRef } from 'react';

export default function Terminal({ containerId }: { containerId: number }) {
  const termRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // eslint-disable-next-line consistent-return
  const connectSocket = useCallback(() => {
    if (!xtermRef.current) return; // bail if we don't have a terminal to connect to.

    // connect to the exec service for the given container.
    const ws = new WebSocket(`/ng/admin/container/${containerId}/exec`);
    const term = xtermRef.current;

    ws.onopen = () => {
      // when socket connects, reset the terminal to remove any disconnected message.
      term.reset();
    };

    ws.onclose = (e) => {
      // when socket closes, show disconnected message.
      term.writeln(`\x1b[0;31mTerminal Disconnected (${e.code})`);
    };

    // start piping data between socket and terminal.
    ws.onmessage = async (event) => {
      term.write(await event.data.text());
    };
    xtermRef.current.onData((data) => {
      ws.send(data);
    });

    socketRef.current = ws;
  }, [ containerId ]);

  useEffect(() => {
    if (!termRef.current) return;

    if (!xtermRef.current) {
      // if we don't have an existing terminal, create it.
      const term = new XTerm({
        fontFamily : 'monospace',
      });

      // setup webgl addon for better performance.
      const webgl = new WebglAddon();
      webgl.onContextLoss(() => {
        webgl.dispose();
      });

      term.loadAddon(webgl);
      term.open(termRef.current);

      // show initial connecting message until socket connects.
      term.writeln('\x1b[0;34mConnecting to terminal...');

      xtermRef.current = term;
    }

    // timeout to debounce socket connection. prevents double socket connections in strict mode.
    const timeout = setTimeout(connectSocket, 100);

    // eslint-disable-next-line consistent-return
    return () => {
      // cancel socket connection if it hasn't happened yet.
      clearTimeout(timeout);

      // clean up socket if it exists.
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }

      // dispose terminal instance.
      if (xtermRef.current) {
        xtermRef.current.dispose();
        xtermRef.current = null;
      }
    };
  }, [ connectSocket ]);

  return (
    <div ref={termRef} className="rounded overflow-clip" />
  );
}
