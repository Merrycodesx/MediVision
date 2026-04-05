import { useState } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/';

export default function Auth({ setCurrentFeature }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('doctor');
  const [message, setMessage] = useState('');

  const handleLogin = async () => {
    if (!email || !password || !role) {
      setMessage('Email, password, and role are required.');
      return;
    }
    setMessage('Logging in...');

    try {
      const resp = await fetch(`${API_BASE}auth/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role }),
      });
      const data = await resp.json();
      if (resp.ok && data.access) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        setMessage('Login successful.');
        setCurrentFeature('patients');
      } else {
        setMessage(data.detail || 'Login failed, check credentials.');
      }
    } catch (error) {
      console.error(error);
      setMessage('Network error while logging in.');
    }
  };

  return (
    <section>
      <h2>Login</h2>
      <label>Email</label><br />
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      /><br />
      <label>Password</label><br />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      /><br />
      <label>Role</label><br />
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="doctor">Doctor</option>
        <option value="clinician">Clinician</option>
        <option value="radiologist">Radiologist</option>
        <option value="admin">Admin</option>
      </select><br />
      <button onClick={handleLogin}>Login</button>
      <button onClick={() => setCurrentFeature('register')} style={{ marginLeft: '8px' }}>Register</button>
      <p>{message}</p>
    </section>
  );
}