const API_BASE = 'http://127.0.0.1:8000/api/';

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

export async function initRegister() {
  document.getElementById('register-cancel').onclick = () => window.loadFeature('auth');
  document.getElementById('register-btn').onclick = async () => {
    const payload = {
      username: document.getElementById('reg-username').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      password: document.getElementById('reg-password').value,
    };
    const msg = document.getElementById('register-message');

    if (!payload.username || !payload.email || !payload.password) {
      msg.textContent = 'Username, email and password are required.';
      return;
    }

    try {
      const resp = await fetch(`${API_BASE}auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (resp.ok) {
        msg.textContent = 'Registration successful. You can now login.';
      } else {
        msg.textContent = data.detail || 'Registration failed.';
      }
    } catch (error) {
      console.error(error);
      msg.textContent = 'Network error during registration.';
    }
  };
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (resp.ok) {
        msg.textContent = 'Registration succeeded. Please login.';
      } else {
        msg.textContent = data.detail || 'Registration failed (check fields).';
      }
    } catch (error) {
      console.error(error);
      msg.textContent = 'Network error on registration.';
    }
  };
}
