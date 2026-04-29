import { useState } from 'react';
import { login, saveSession } from '../lib/api';

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
      const data = await login(email, password, role);
      saveSession(data);
      setMessage(`Login successful${data.hospital_name ? ` at ${data.hospital_name}` : ''}.`);
      setCurrentFeature('patients');
    } catch (error) {
      console.error(error);
      setMessage(error.message || 'Login failed, check credentials.');
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
        <option value="auditor">Auditor</option>
      </select><br />
      <button onClick={handleLogin}>Login</button>
      <button onClick={() => setCurrentFeature('register')} style={{ marginLeft: '8px' }}>Register</button>
      <p>{message}</p>
    </section>
  );
}
