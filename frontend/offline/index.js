export function initOffline() {
  const indicator = document.createElement('div');
  indicator.id = 'offline-indicator';
  indicator.style.position = 'fixed';
  indicator.style.bottom = '10px';
  indicator.style.right = '10px';
  indicator.style.padding = '6px 10px';
  indicator.style.borderRadius = '4px';
  indicator.style.color = '#fff';
  indicator.style.fontSize = '12px';
  const update = () => {
    const offline = !navigator.onLine;
    indicator.textContent = offline ? 'Offline mode' : 'Online mode';
    indicator.style.background = offline ? '#cc0000' : '#00aa00';
  };
  update();
  window.addEventListener('online', update);
  window.addEventListener('offline', update);
  document.body.appendChild(indicator);
}
