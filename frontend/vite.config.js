import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,      // same as 0.0.0.0, exposes to port-forwarding proxy
    port: 5173       // keep consistent with the forwarded port
  },
})
