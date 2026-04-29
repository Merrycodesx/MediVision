import { useState } from 'react';
import { registerUser } from '../lib/api';

export default function Register({ setCurrentFeature }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('clinician');
  const [hospitalCode, setHospitalCode] = useState('');
  const [hospitalName, setHospitalName] = useState('');
  const [message, setMessage] = useState('');

  const handleRegister = async () => {
    if (!username || !email || !password) {
      setMessage('Username, email and password are required.');
      return;
    }

    try {
      await registerUser({
        username,
        email,
        password,
        role,
        hospital_code: hospitalCode,
        hospital_name: hospitalName,
      });
      setMessage('Registration successful. You can now login.');
      setUsername('');
      setEmail('');
      setPassword('');
      setHospitalCode('');
      setHospitalName('');
    } catch (error) {
      console.error(error);
      setMessage(error.message || 'Registration failed.');
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
      <label>Role</label><br />
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="clinician">Clinician</option>
        <option value="radiologist">Radiologist</option>
        <option value="admin">Admin</option>
        <option value="auditor">Auditor</option>
      </select><br />
      <label>Hospital Code</label><br />
      <input
        value={hospitalCode}
        onChange={(e) => setHospitalCode(e.target.value)}
        placeholder="Existing code, or new code for admin bootstrap"
      /><br />
      <label>Hospital Name</label><br />
      <input
        value={hospitalName}
        onChange={(e) => setHospitalName(e.target.value)}
        placeholder="Hospital name"
      /><br />
      <button onClick={handleRegister}>Register</button>
      <button onClick={() => setCurrentFeature('auth')} style={{ marginLeft: '8px' }}>Cancel</button>
      <p>{message}</p>
    </section>
  );
}
