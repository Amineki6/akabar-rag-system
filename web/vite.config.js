import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        // Defines your main page using index.html
        main: resolve(__dirname, 'index.html'),
        // Defines your about page using about.html
        about: resolve(__dirname, 'about.html'),
      },
    },
  },
  server: {
    proxy: {
      // String shorthand for simple proxy
      '/api': {
        target: 'http://localhost:8070', // Your Python backend address
        changeOrigin: true,
        secure: false,      
      },
    },
  },
})