import { enqueueOfflineAction } from '../offline/index.js';

const API_BASE = 'http://127.0.0.1:8000/api/';

export function labUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Laboratory Data</h2>
    <input id="lab-patient-id" placeholder="Patient ID" /><br>
    <input id="lab-genexpert" placeholder="GeneXpert result" /><br>
    <input id="lab-smear" placeholder="Smear microscopy result" /><br>
    <input id="lab-culture" placeholder="Culture result" /><br>
    <button id="lab-save">Save Lab Data</button>
    <p id="lab-message"></p>
    <button id="lab-back">Back</button>
  `;
  return section;
}

export async function initLab() {
  document.getElementById('lab-back').onclick = () => window.loadFeature('patients');

  document.getElementById('lab-save').onclick = async () => {
    const patient_id = document.getElementById('lab-patient-id').value;
    const genexpert = document.getElementById('lab-genexpert').value;
    const smear = document.getElementById('lab-smear').value;
    const culture = document.getElementById('lab-culture').value;
    const msg = document.getElementById('lab-message');

    if (!patient_id || !genexpert) {
      msg.textContent = 'Patient ID and GeneXpert are required';
      return;
    }

    const payload = { patient_id, genexpert, smear, culture };

    if (!navigator.onLine) {
      enqueueOfflineAction('labs/', 'POST', payload);
      msg.textContent = 'Offline: lab data queued for sync.';
      return;
    }

    try {
      const resp = await fetch(`${API_BASE}labs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (resp.ok) {
        msg.textContent = 'Lab result saved';
      } else {
        enqueueOfflineAction('labs/', 'POST', payload);
        msg.textContent = data.detail || 'Failed to save lab result; queued for retry';
      }
    } catch (error) {
      console.error(error);
      enqueueOfflineAction('labs/', 'POST', payload);
      msg.textContent = 'Network error; lab data queued for retry';
    }
  };
}
