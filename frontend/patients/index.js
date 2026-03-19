const API_BASE = 'http://127.0.0.1:8000/api/';

export function patientsUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Patient Management</h2>
    <div style="margin-bottom: 8px;">
      <button id="btn-refresh">Load Patients</button>
      <button id="btn-add">Add Patient</button>
      <button id="btn-cxr">CXR</button>
      <button id="btn-lab">Lab</button>
      <button id="btn-fusion">Fusion</button>
      <button id="btn-report">Reports</button>
      <button id="btn-user-mgmt">User Mgmt</button>
      <button id="btn-logout">Logout</button>
    </div>
    <ul id="patient-list"></ul>
    <div id="patient-detail"></div>
    <div id="patient-form" style="margin-top: 16px;"></div>
  `;
  return section;
}

function getToken() {
  return localStorage.getItem('accessToken');
}

export async function initPatients() {
  const list = document.getElementById('patient-list');
  const patientForm = document.getElementById('patient-form');
  const msg = document.createElement('p');
  patientForm.appendChild(msg);

  async function loadPatients() {
    list.innerHTML = 'Loading...';
    try {
      const resp = await fetch(`${API_BASE}patients/`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (!resp.ok) {
        list.innerHTML = 'Failed to load patients';
        return;
      }
      const patients = await resp.json();
      list.innerHTML = '';
      patients.forEach(p => {
        const li = document.createElement('li');
        li.textContent = `${p.full_name} (Age ${p.age}) [${p.sex}]`;
        li.style.cursor = 'pointer';
        li.onclick = () => displayPatient(p);
        list.appendChild(li);
      });
    } catch (error) {
      console.error(error);
      list.innerHTML = 'Error loading patients';
    }
  }

  async function displayPatient(patient) {
    const detail = document.getElementById('patient-detail');
    detail.innerHTML = `
      <h3>Selected patient: ${patient.full_name}</h3>
      <pre>${JSON.stringify(patient, null, 2)}</pre>
      <button id="edit-patient">Edit</button>
      <button id="delete-patient" style="margin-left: 8px;">Delete</button>
    `;
    document.getElementById('edit-patient').onclick = () => showEditPatient(patient);
    document.getElementById('delete-patient').onclick = () => deletePatient(patient.id);
  }

  function showEditPatient(patient) {
    patientForm.innerHTML = `
      <h3>Edit patient</h3>
      <input id="edit-fullname" value="${patient.full_name}" placeholder="Full Name" /><br>
      <input id="edit-age" type="number" value="${patient.age}" placeholder="Age" /><br>
      <select id="edit-sex">
        <option value="M" ${patient.sex === 'M' ? 'selected' : ''}>Male</option>
        <option value="F" ${patient.sex === 'F' ? 'selected' : ''}>Female</option>
      </select><br>
      <label><input id="edit-hiv" type="checkbox" ${patient.hiv_Status ? 'checked' : ''} /> HIV Positive</label><br>
      <input id="edit-symptoms" value="${patient.symptoms?.join(', ') || ''}" placeholder="Symptoms" /><br>
      <button id="update-patient">Save</button>
    `;

    document.getElementById('update-patient').onclick = async () => {
      const payload = {
        full_name: document.getElementById('edit-fullname').value,
        age: parseInt(document.getElementById('edit-age').value, 10),
        sex: document.getElementById('edit-sex').value,
        hiv_Status: document.getElementById('edit-hiv').checked,
        symptoms: document.getElementById('edit-symptoms').value.split(',').map(s => s.trim()).filter(Boolean),
      };
      const resp = await fetch(`${API_BASE}patients/${patient.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        msg.textContent = 'Patient updated successfully';
        loadPatients();
      } else {
        msg.textContent = 'Failed to update patient';
      }
    };
  }

  async function deletePatient(id) {
    const resp = await fetch(`${API_BASE}patients/${id}/`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (resp.ok) {
      msg.textContent = 'Patient deleted';
      loadPatients();
      document.getElementById('patient-detail').innerHTML = '';
    } else {
      msg.textContent = 'Failed to delete patient';
    }
  }

  function showCreateForm() {
    patientForm.innerHTML = `
      <h3>Create new patient</h3>
      <input id="new-fullname" placeholder="Full Name" /><br>
      <input id="new-age" type="number" placeholder="Age" /><br>
      <select id="new-sex"><option value="M">Male</option><option value="F">Female</option></select><br>
      <label><input id="new-hiv" type="checkbox" /> HIV Positive</label><br>
      <input id="new-symptoms" placeholder="Symptoms (comma-separated)" /><br>
      <button id="create-patient">Create</button>
    `;

    document.getElementById('create-patient').onclick = async () => {
      const payload = {
        full_name: document.getElementById('new-fullname').value,
        age: parseInt(document.getElementById('new-age').value, 10),
        sex: document.getElementById('new-sex').value,
        hiv_Status: document.getElementById('new-hiv').checked,
        symptoms: document.getElementById('new-symptoms').value.split(',').map(s => s.trim()).filter(Boolean),
      };
      const resp = await fetch(`${API_BASE}patients/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        msg.textContent = 'Patient created';
        loadPatients();
      } else {
        const err = await resp.text();
        msg.textContent = 'Failed to create patient: ' + err;
      }
    };
  }

  document.getElementById('btn-refresh').onclick = loadPatients;
  document.getElementById('btn-add').onclick = showCreateForm;
  document.getElementById('btn-cxr').onclick = () => window.loadFeature('cxr');
  document.getElementById('btn-lab').onclick = () => window.loadFeature('lab');
  document.getElementById('btn-fusion').onclick = () => window.loadFeature('fusion');
  document.getElementById('btn-report').onclick = () => window.loadFeature('reporting');
  document.getElementById('btn-user-mgmt').onclick = () => window.loadFeature('userManagement');
  document.getElementById('btn-logout').onclick = () => {
    localStorage.clear();
    window.loadFeature('auth');
  };

  list.innerHTML = '';
  loadPatients();
}
