import react from '@vitejs/plugin-react'
import { networkInterfaces } from 'node:os'
import { defineConfig } from 'vite'

// Detect this machine's LAN IPv4 so QR codes/share links work from phones on the same Wi-Fi.
function getLanIp(): string {
  if (process.env.LAN_IP) return process.env.LAN_IP
  const candidates: string[] = []
  for (const [name, ifaces] of Object.entries(networkInterfaces())) {
    if (/^(docker|br-|veth|virbr|lo|tun|tap|wg)/.test(name)) continue
    for (const iface of ifaces ?? []) {
      if (iface.family === 'IPv4' && !iface.internal) candidates.push(iface.address)
    }
  }
  return candidates.find((ip) => ip.startsWith('192.168.')) ?? candidates[0] ?? 'localhost'
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    __LAN_IP__: JSON.stringify(getLanIp()),
  },
  server: {
    host: true, // listen on 0.0.0.0 so other devices on the LAN can connect
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
