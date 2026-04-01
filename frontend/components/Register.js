import { useState } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/';

export default function Register({ setCurrentFeature }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleRegister = async () => {
    if (!username || !email || !password) {
      setMessage('Username, email and password are required.');
      return;
    }

    try {
      const resp = await fetch(`${API_BASE}auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await resp.json();
      if (resp.ok) {
        setMessage('Registration successful. You can now login.');
      } else {
        setMessage(data.detail || 'Registration failed.');
      }
    } catch (error) {
      console.error(error);
      setMessage('Network error during registration.');
    }
  };

  return (
    <section>
      <h2>User Registration</h2>
      <label>Username</label><br />
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      /><br />
      <label>Email</label><br />
      <input
        type="email"
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
      <button onClick={handleRegister}>Register</button>
      <button onClick={() => setCurrentFeature('auth')} style={{ marginLeft: '8px' }}>Cancel</button>
      <p>{message}</p>
    </section>
  );
}