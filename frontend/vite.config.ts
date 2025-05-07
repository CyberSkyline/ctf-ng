import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  server : {
    allowedHosts : [ '.cyberskyline.com', '.localhost' ],
    host : '0.0.0.0',
    cors : true,
    hmr : {
      port : 5173,
      protocol : 'ws',
      clientPort : 5173,
    },
  },
  base : '/static/',
  plugins: [
    react(),
  ],
});
