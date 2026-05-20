import { useState, useEffect } from 'react';

export default function Offline() {
  // Must match SSR: navigator is undefined on the server. Sync onLine only after mount
  // so the first client paint matches the server HTML (avoids hydration errors).
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div style={{ position: 'fixed', bottom: '10px', right: '10px', padding: '5px', background: isOnline ? 'green' : 'red', color: 'white' }}>
      {isOnline ? 'Online' : 'Offline'}
    </div>
  );
}