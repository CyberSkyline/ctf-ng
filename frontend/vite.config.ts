import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { spawnSync } from 'child_process';
import path from 'path';
import { defineConfig } from 'vite';

function gitStatus(...args: string[]) {
  return spawnSync('git', args, { cwd : __dirname }).stdout.toString().trim();
}

const [ long ] = gitStatus('log', '--no-color', '-n', '1', '--pretty=format:%H%n%aI%n%s').split('\n');

const RELEASE = long;

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  define : {
    BUILD_MODE : command === 'build',
    RELEASE : JSON.stringify(RELEASE),
    BASE_PATH : JSON.stringify(command === 'build' ? '/ctf' : ''),
    PUBLIC_BASE : JSON.stringify(command === 'build' ? '/dist' : '/static'),
  },
  server : {
    allowedHosts : [ '.cisa.gov', '.localhost' ],
    host : '0.0.0.0',
    cors : true,
    hmr : {
      port : 5173,
      protocol : 'ws',
      clientPort : 5173,
    },
  },
  base : command === 'build' ? '/dist/' : '/static/',
  plugins : [
    react(),
    tailwindcss(),
    {
      // Force full page reload when socket implementation changes.
      // Ensures that old sockets and event listeners are cleaned up.
      name : 'full-reload-socket',
      handleHotUpdate({ file, server }) {
        if (file.endsWith('socket.ts')) {
          server.ws.send({ type : 'full-reload' });
          return [];
        }
        return undefined;
      },
    },
  ],
  resolve : {
    alias : {
      assets : path.resolve(__dirname, './src/assets'),
      components : path.resolve(__dirname, './src/components'),
      routes : path.resolve(__dirname, './src/routes'),
      '@' : path.resolve(__dirname, './src'),
    },
  },
  build : {
    cssCodeSplit : false,
    rollupOptions : {
      output : {
        entryFileNames : `${RELEASE}/[name].js`,
        chunkFileNames : `${RELEASE}/[name].js`,
        assetFileNames : `${RELEASE}/[name][extname]`,
      },
    },
  },
  optimizeDeps : {
    include : [ 'react', 'react-dom', 'react-router-dom' ],
  },
  publicDir : 'public',
}));
