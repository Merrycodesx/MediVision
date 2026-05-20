const API_BASE = (typeof window !== 'undefined' && window.API_BASE_URL)
  ? String(window.API_BASE_URL).replace(/\/$/, '') + '/'
  : 'http://127.0.0.1:8000/api/';

export function registerUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>User Registration</h2>
    <label>Username</label><br>
    <input id="reg-username" placeholder="Username" /><br>
    <label>Email</label><br>
    <input id="reg-email" type="email" placeholder="Email" /><br>
    <label>Password</label><br>
    <input id="reg-password" type="password" placeholder="Password" /><br>
    <button id="register-btn">Register</button>
    <button id="register-cancel" style="margin-left: 8px;">Cancel</button>
    <p id="register-message"></p>
  `;
  return section;
}

function formatRegisterError(data) {
  if (!data) return 'Registration failed.';
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) return data.join('; ');
  return Object.entries(data)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join('; ') : value}`)
    .join(' | ');
}

export async function initRegister() {
  const cancelButton = document.getElementById('register-cancel');
  const registerButton = document.getElementById('register-btn');
  const msg = document.getElementById('register-message');

  cancelButton.onclick = () => window.loadFeature('auth');
  registerButton.onclick = async () => {
    const payload = {
      username: document.getElementById('reg-username').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      password: document.getElementById('reg-password').value,
    };

    msg.textContent = '';
    if (!payload.username || !payload.email || !payload.password) {
      msg.textContent = 'Username, email and password are required.';
      return;
    }

    registerButton.disabled = true;
    try {
      const url = `${API_BASE}auth/register/`;
      console.debug('[Register] Request', { url, body: payload });
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const text = await resp.text();
      let data = null;
      if (text) {
        try {
          data = JSON.parse(text);
        } catch {
          data = text;
        }
      }
      console.debug('[Register] Response', { url, status: resp.status, data });

      if (resp.ok) {
        msg.textContent = 'Registration successful. You can now login.';
      } else {
        msg.textContent = data?.detail || data?.message || formatRegisterError(data);
      }
    } catch (error) {
      console.error('[Register] Network error', error);
      msg.textContent = 'Network error during registration. Check backend availability.';
    } finally {
      registerButton.disabled = false;
    }
  };
}
