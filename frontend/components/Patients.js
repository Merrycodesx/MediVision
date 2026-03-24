import { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/';

function getToken() {
  return localStorage.getItem('accessToken');
}

export default function Patients({ setCurrentFeature }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [isAdding, setIsAdding] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}patients/`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (!resp.ok) {
        setMessage('Failed to load patients');
        return;
      }
      const data = await resp.json();
      setPatients(data);
      setMessage('');
    } catch (error) {
      console.error(error);
      setMessage('Error loading patients');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPatient = (patient) => {
    setSelectedPatient(patient);
    setIsEditing(false);
    setIsAdding(false);
  };

  const handleAdd = () => {
    setIsAdding(true);
    setIsEditing(false);
    setSelectedPatient(null);
    setName('');
    setAge('');
  };

  const handleEdit = () => {
    if (!selectedPatient) return;
    setIsEditing(true);
    setIsAdding(false);
    setName(selectedPatient.name);
    setAge(selectedPatient.age);
  };

  const handleSave = async () => {
    const payload = { name, age: parseInt(age, 10) };
    let url = `${API_BASE}patients/`;
    let method = 'POST';
    if (isEditing && selectedPatient) {
      url += `${selectedPatient.id}/`;
      method = 'PUT';
    }
    try {
      const resp = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        setMessage(isEditing ? 'Patient updated successfully' : 'Patient added successfully');
        loadPatients();
        setIsAdding(false);
        setIsEditing(false);
        setSelectedPatient(null);
      } else {
        setMessage('Failed to save patient');
      }
    } catch (error) {
      console.error(error);
      setMessage('Error saving patient');
    }
  };

  const handleDelete = async () => {
    if (!selectedPatient) return;
    try {
      const resp = await fetch(`${API_BASE}patients/${selectedPatient.id}/`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (resp.ok) {
        setMessage('Patient deleted successfully');
        loadPatients();
        setSelectedPatient(null);
      } else {
        setMessage('Failed to delete patient');
      }
    } catch (error) {
      console.error(error);
      setMessage('Error deleting patient');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setCurrentFeature('auth');
  };

  return (
    <section>
      <h2>Patient Management</h2>
      <div style={{ marginBottom: '8px' }}>
        <button onClick={loadPatients}>Load Patients</button>
        <button onClick={handleAdd}>Add Patient</button>
        <button onClick={() => setCurrentFeature('cxr')}>CXR</button>
        <button onClick={() => setCurrentFeature('lab')}>Lab</button>
        <button onClick={() => setCurrentFeature('fusion')}>Fusion</button>
        <button onClick={() => setCurrentFeature('reporting')}>Reports</button>
        <button onClick={() => setCurrentFeature('userManagement')}>User Mgmt</button>
        <button onClick={handleLogout}>Logout</button>
      </div>
      {loading && <p>Loading...</p>}
      <ul>
        {patients.map(p => (
          <li key={p.id} onClick={() => handleSelectPatient(p)} style={{ cursor: 'pointer' }}>
            {p.name} (Age {p.age})
          </li>
        ))}
      </ul>
      {selectedPatient && (
        <div>
          <h3>Selected patient: {selectedPatient.name}</h3>
          <pre>{JSON.stringify(selectedPatient, null, 2)}</pre>
          <button onClick={handleEdit}>Edit</button>
          <button onClick={handleDelete} style={{ marginLeft: '8px' }}>Delete</button>
        </div>
      )}
      {(isAdding || isEditing) && (
        <div style={{ marginTop: '16px' }}>
          <h3>{isEditing ? 'Edit patient' : 'Add patient'}</h3>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
          /><br />
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            placeholder="Age"
          /><br />
          <button onClick={handleSave}>Save</button>
        </div>
      )}
      <p>{message}</p>
    </section>
  );
}