import { useEffect, useState } from 'react';
import {
  createPatient,
  deletePatient,
  getPatient,
  getPatients,
  logout,
  runInference,
  updatePatient,
} from '../lib/api';

const emptyPatient = {
  name: '',
  age: '',
  sex: 'male',
  hiv_status: false,
  symptoms: '',
  comorbidities: '',
};

export default function Patients({ setCurrentFeature }) {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [form, setForm] = useState(emptyPatient);
  const [editing, setEditing] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadPatients();
  }, [page]);

  async function loadPatients(nextSearch = search) {
    setMessage('Loading patients...');
    try {
      const query = `?page=${page}&limit=10${nextSearch ? `&search=${encodeURIComponent(nextSearch)}` : ''}`;
      const data = await getPatients(query);
      setPatients(data.results || []);
      setMessage('');
    } catch (error) {
      setMessage(error.message);
    }
  }

  function payloadFromForm() {
    return {
      name: form.name,
      age: Number(form.age),
      sex: form.sex,
      hiv_status: Boolean(form.hiv_status),
      symptoms: form.symptoms.split(',').map((item) => item.trim()).filter(Boolean),
      comorbidities: form.comorbidities.split(',').map((item) => item.trim()).filter(Boolean),
    };
  }

  function startCreate() {
    setEditing(false);
    setSelectedPatient(null);
    setForm(emptyPatient);
    setMessage('');
  }

  function startEdit(patient) {
    setEditing(true);
    setSelectedPatient(patient);
    setForm({
      name: patient.name || '',
      age: patient.age || '',
      sex: patient.sex || 'male',
      hiv_status: Boolean(patient.hiv_status),
      symptoms: Array.isArray(patient.symptoms) ? patient.symptoms.join(', ') : '',
      comorbidities: Array.isArray(patient.comorbidities) ? patient.comorbidities.join(', ') : '',
    });
  }

  async function savePatient() {
    if (!form.name || !form.age) {
      setMessage('Name and age are required.');
      return;
    }

    try {
      if (editing && selectedPatient) {
        await updatePatient(selectedPatient.id, payloadFromForm());
        setMessage('Patient update sent.');
      } else {
        await createPatient(payloadFromForm());
        setMessage('Patient created.');
      }
      setForm(emptyPatient);
      setEditing(false);
      await loadPatients();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function selectPatient(patient) {
    try {
      const detail = await getPatient(patient.id);
      setSelectedPatient(detail);
      setMessage('');
    } catch (error) {
      setSelectedPatient(patient);
      setMessage(error.message);
    }
  }

  async function removePatient() {
    if (!selectedPatient) return;
    try {
      await deletePatient(selectedPatient.id);
      setMessage('Patient delete sent.');
      setSelectedPatient(null);
      await loadPatients();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function inferPatient() {
    if (!selectedPatient) return;
    try {
      const result = await runInference({
        patient_id: selectedPatient.id,
        age: selectedPatient.age,
        sex: selectedPatient.sex,
      });
      setMessage(`Inference complete: ${result.tb_score}% - ${result.triage_recommendation}`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  function signOut() {
    logout();
    setCurrentFeature('auth');
  }

  return (
    <main>
      <div className="topbar">
        <div>
          <h2>Patients</h2>
          <p className="muted">Create, search, inspect, and send patients into the TB workflow.</p>
        </div>
        <button onClick={signOut}>Logout</button>
      </div>

      <nav className="toolbar">
        <button onClick={() => setCurrentFeature('screenings')}>Diagnostics</button>
        <button onClick={() => setCurrentFeature('userManagement')}>Users</button>
        <button onClick={() => setCurrentFeature('admin')}>Admin Tools</button>
        <button onClick={startCreate}>New Patient</button>
      </nav>

      <section className="grid">
        <div className="panel">
          <div className="inline">
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or age" />
            <button onClick={() => loadPatients(search)}>Search</button>
          </div>
          <ul className="list">
            {patients.map((patient) => (
              <li key={patient.id} onClick={() => selectPatient(patient)}>
                <strong>{patient.name}</strong>
                <span>{patient.age} years, {patient.sex}</span>
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
          <h3>{editing ? 'Edit Patient' : 'New Patient'}</h3>
          <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Full name" />
          <input type="number" value={form.age} onChange={(event) => setForm({ ...form, age: event.target.value })} placeholder="Age" />
          <select value={form.sex} onChange={(event) => setForm({ ...form, sex: event.target.value })}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
          <label className="check">
            <input type="checkbox" checked={form.hiv_status} onChange={(event) => setForm({ ...form, hiv_status: event.target.checked })} />
            HIV positive
          </label>
          <input value={form.symptoms} onChange={(event) => setForm({ ...form, symptoms: event.target.value })} placeholder="Symptoms, comma separated" />
          <input value={form.comorbidities} onChange={(event) => setForm({ ...form, comorbidities: event.target.value })} placeholder="Comorbidities, comma separated" />
          <button onClick={savePatient}>{editing ? 'Save Changes' : 'Create Patient'}</button>
        </div>
      </section>

      {selectedPatient && (
        <section className="panel">
          <h3>Selected Patient</h3>
          <pre>{JSON.stringify(selectedPatient, null, 2)}</pre>
          <div className="toolbar">
            <button onClick={() => startEdit(selectedPatient)}>Edit</button>
            <button onClick={removePatient}>Delete</button>
            <button onClick={inferPatient}>Run Inference</button>
          </div>
        </section>
      )}

      {message && <p className="message">{message}</p>}
    </main>
  );
}
