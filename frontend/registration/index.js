const API_BASE = 'http://127.0.0.1:8000/api/';

export function registerUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>User Registration</h2>
    <input id="reg-email" type="email" placeholder="Email" /><br>
    <input id="reg-username" placeholder="Username" /><br>
    <input id="reg-first-name" placeholder="First Name" /><br>
    <input id="reg-last-name" placeholder="Last Name" /><br>
    <input id="reg-native-name" placeholder="Native Name" /><br>
    <input id="reg-phone" placeholder="Phone" /><br>
    <input id="reg-password" type="password" placeholder="Password" /><br>
    <select id="reg-role">
      <option value="C">Clinician</option>
      <option value="R">Radiologist</option>
      <option value="L">Local Admin</option>
      <option value="A">Auditor</option>
      <option value="P">Patient</option>
    </select><br>
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
      email: document.getElementById('reg-email').value.trim(),
      username: document.getElementById('reg-username').value.trim(),
      first_name: document.getElementById('reg-first-name').value.trim(),
      last_name: document.getElementById('reg-last-name').value.trim(),
      native_name: document.getElementById('reg-native-name').value.trim(),
      phone_num: document.getElementById('reg-phone').value.trim(),
      password: document.getElementById('reg-password').value,
      role: document.getElementById('reg-role').value,
    };
    const msg = document.getElementById('register-message');

    if (!payload.email || !payload.username || !payload.password) {
      msg.textContent = 'Email, username and password are required.';
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
