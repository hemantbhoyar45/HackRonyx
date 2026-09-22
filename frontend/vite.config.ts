import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      { find: /^leaflet-draw$/, replacement: path.resolve(import.meta.dirname, 'src/leaflet-draw-shim.js') }
    ]
  },
  optimizeDeps: {
    include: ['react-leaflet-draw', 'leaflet-draw']
  }
})
