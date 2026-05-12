import { useEffect, useState } from 'react';
import { createUser, deleteUser, listUsers, updateUser } from '../lib/api';

const emptyUser = {
  email: '',
  username: '',
  password: '',
  role: 'clinician',
  first_name: '',
  last_name: '',
  native_name: '',
  phone_num: '',
  is_active: true,
};

export default function UserManagement({ setCurrentFeature }) {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [form, setForm] = useState(emptyUser);
  const [page, setPage] = useState(1);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadUsers();
  }, [page]);

  async function loadUsers() {
    try {
      const data = await listUsers(`?page=${page}&limit=20`);
      setUsers(data.results || []);
      setMessage('');
    } catch (error) {
      setMessage(error.message);
    }
  }

  function editUser(user) {
    setSelectedUser(user);
    setForm({
      ...emptyUser,
      ...user,
      password: '',
      role: user.role || 'clinician',
    });
  }

  async function saveUser() {
    try {
      const payload = { ...form };
      if (!payload.password) delete payload.password;
      if (selectedUser) {
        await updateUser(selectedUser.id, payload);
        setMessage('User update sent.');
      } else {
        await createUser(payload);
        setMessage('User created.');
      }
      setForm(emptyUser);
      setSelectedUser(null);
      await loadUsers();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function removeUser() {
    if (!selectedUser) return;
    try {
      await deleteUser(selectedUser.id);
      setMessage('User deleted.');
      setSelectedUser(null);
      setForm(emptyUser);
      await loadUsers();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main>
      <div className="topbar">
        <h2>User Management</h2>
        <button onClick={() => setCurrentFeature('patients')}>Back</button>
      </div>

      <section className="grid">
        <div className="panel">
          <h3>Hospital Users</h3>
          <ul className="list">
            {users.map((user) => (
              <li key={user.id} onClick={() => editUser(user)}>
                <strong>{user.email}</strong>
                <span>{user.role} - {user.is_active ? 'active' : 'inactive'}</span>
              </li>
            ))}
          </ul>
          <div className="inline">
            <button onClick={() => setPage(Math.max(1, page - 1))}>Previous</button>
            <span>Page {page}</span>
            <button onClick={() => setPage(page + 1)}>Next</button>
          </div>
        </div>

        <div className="panel">
          <h3>{selectedUser ? 'Edit User' : 'Create User'}</h3>
          <input value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} placeholder="Email" />
          <input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="Username" />
          <input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder={selectedUser ? 'New password (optional)' : 'Password'} />
          <select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}>
            <option value="clinician">Clinician</option>
            <option value="radiologist">Radiologist</option>
            <option value="admin">Admin</option>
            <option value="auditor">Auditor</option>
          </select>
          <input value={form.first_name || ''} onChange={(event) => setForm({ ...form, first_name: event.target.value })} placeholder="First name" />
          <input value={form.last_name || ''} onChange={(event) => setForm({ ...form, last_name: event.target.value })} placeholder="Last name" />
          <input value={form.native_name || ''} onChange={(event) => setForm({ ...form, native_name: event.target.value })} placeholder="Native name" />
          <input value={form.phone_num || ''} onChange={(event) => setForm({ ...form, phone_num: event.target.value })} placeholder="Phone number" />
          <label className="check">
            <input type="checkbox" checked={Boolean(form.is_active)} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />
            Active
          </label>
          <div className="toolbar">
            <button onClick={saveUser}>{selectedUser ? 'Save User' : 'Create User'}</button>
            <button onClick={() => { setSelectedUser(null); setForm(emptyUser); }}>New</button>
            {selectedUser && <button onClick={removeUser}>Delete</button>}
          </div>
        </div>
      </section>

      {message && <p className="message">{message}</p>}
    </main>
  );
}
