const OFFLINE_QUEUE_KEY = 'offlineQueue';

function getOfflineQueue() {
  const raw = localStorage.getItem(OFFLINE_QUEUE_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function setOfflineQueue(queue) {
  localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
}

export function enqueueOfflineAction(path, method, body) {
  const queue = getOfflineQueue();
  queue.push({ path, method, body, addedAt: new Date().toISOString() });
  setOfflineQueue(queue);
}

export async function syncOfflineQueue() {
  const queue = getOfflineQueue();
  if (!queue.length || !navigator.onLine) return;

  const remaining = [];
  for (const item of queue) {
    try {
      const token = localStorage.getItem('accessToken');
      const resp = await fetch(`http://127.0.0.1:8000/api/${item.path}`, {
        method: item.method,
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(item.body),
      });

      if (!resp.ok) {
        remaining.push(item);
      }
    } catch (error) {
      console.error('Sync failed for queue item:', item, error);
      remaining.push(item);
    }
  }

  setOfflineQueue(remaining);
  const indicator = document.getElementById('offline-indicator');
  if (indicator) {
    indicator.textContent = remaining.length ? `Sync pending: ${remaining.length}` : 'Online mode';
    indicator.style.background = remaining.length ? '#ff8c00' : '#00aa00';
  }
}

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

  const updateIndicator = () => {
    const offline = !navigator.onLine;
    const queue = getOfflineQueue();
    if (offline) {
      indicator.textContent = `Offline mode (queued: ${queue.length})`;
      indicator.style.background = '#cc0000';
    } else if (queue.length > 0) {
      indicator.textContent = `Sync pending: ${queue.length}`;
      indicator.style.background = '#ff8c00';
    } else {
      indicator.textContent = 'Online mode';
      indicator.style.background = '#00aa00';
    }
  };

  updateIndicator();
  window.addEventListener('online', async () => {
    updateIndicator();
    await syncOfflineQueue();
    updateIndicator();
  });
  window.addEventListener('offline', updateIndicator);

  document.body.appendChild(indicator);
  setInterval(async () => {
    if (navigator.onLine) {
      await syncOfflineQueue();
      updateIndicator();
    }
  }, 15000);
}

