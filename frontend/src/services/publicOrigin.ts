declare const __LAN_IP__: string;

/**
 * Origin to embed in QR codes / share links.
 * Priority: VITE_PUBLIC_ORIGIN env > LAN IP (when browsing via localhost) > current origin.
 */
export function getPublicOrigin(): string {
  const configured = import.meta.env.VITE_PUBLIC_ORIGIN as string | undefined;
  if (configured) return configured.replace(/\/$/, '');

  const { protocol, hostname, port, origin } = window.location;
  const isLoopback = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1';
  const lanIp = typeof __LAN_IP__ !== 'undefined' ? __LAN_IP__ : 'localhost';
  if (isLoopback && lanIp && lanIp !== 'localhost') {
    return `${protocol}//${lanIp}${port ? `:${port}` : ''}`;
  }
  return origin;
}
