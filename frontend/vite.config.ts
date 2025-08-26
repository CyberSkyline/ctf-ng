import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
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
  base : '/static/',
  plugins : [ react(), tailwindcss() ],
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
        entryFileNames : '[name].js',
        chunkFileNames : '[name].js',
        assetFileNames : '[name][extname]',
      },
    },
  },
  optimizeDeps : {
    include : [ 'react', 'react-dom', 'react-router-dom' ],
  },
});
