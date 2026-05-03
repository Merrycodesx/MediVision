const API_BASE = 'http://127.0.0.1:8000/api/';

export function authUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Login</h2>
    <label>Username</label><br>
    <input id="login-username" placeholder="Username" /><br>
    <label>Password</label><br>
    <input id="login-password" type="password" placeholder="Password" /><br>
    <button id="login-button">Login</button>
    <button id="go-register" style="margin-left: 8px;">Register</button>
    <p id="login-message"></p>
  `;
  return section;
}

export async function initAuth() {
  const loginButton = document.getElementById('login-button');
  const registerButton = document.getElementById('go-register');
  const msg = document.getElementById('login-message');

  loginButton.onclick = async () => {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    if (!username || !password) {
      msg.textContent = 'Username and password are required.';
      return;
    }
    msg.textContent = 'Logging in...';

    try {
      const resp = await fetch(`${API_BASE}auth/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await resp.json();
      if (resp.ok && data.access) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        msg.textContent = 'Login successful.';
        window.loadFeature('patients');
      } else {
        msg.textContent = data.detail || 'Login failed, check credentials.';
      }
    } catch (error) {
      console.error(error);
      msg.textContent = 'Network error while logging in.';
    }
  };

  registerButton.onclick = () => {
    window.loadFeature('register');
  };
}
