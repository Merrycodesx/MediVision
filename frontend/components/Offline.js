import { useState, useEffect } from 'react';

export default function Offline() {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
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