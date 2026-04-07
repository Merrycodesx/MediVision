import { useState } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/';

export default function Auth({ setCurrentFeature }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleLogin = async () => {
    if (!username || !password) {
      setMessage('Username and password are required.');
      return;
    }
    setMessage('Logging in...');

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
      <label>Username</label><br />
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      /><br />
      <label>Password</label><br />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      /><br />
      <button onClick={handleLogin}>Login</button>
      <button onClick={() => setCurrentFeature('register')} style={{ marginLeft: '8px' }}>Register</button>
      <p>{message}</p>
    </section>
  );
}