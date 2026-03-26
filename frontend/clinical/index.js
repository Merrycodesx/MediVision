import { enqueueOfflineAction } from '../offline/index.js';

const API_BASE = 'http://127.0.0.1:8000/api/';

export function clinicalUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Clinical Data Entry</h2>
    <input id="clinical-patient-id" placeholder="Patient ID" /><br>
    <textarea id="clinical-symptoms" placeholder="Symptoms (comma-separated)" rows="3"></textarea><br>
    <textarea id="clinical-risk-factors" placeholder="Risk factors (comma-separated)" rows="2"></textarea><br>
    <input id="clinical-age" placeholder="Age" type="number" /><br>
    <select id="clinical-sex">
      <option value="M">Male</option>
      <option value="F">Female</option>
    </select><br>
    <label><input id="clinical-smoker" type="checkbox" /> Smoker</label><br>
    <label><input id="clinical-hiv" type="checkbox" /> HIV Positive</label><br>
    <button id="clinical-save">Save Clinical Data</button>
    <p id="clinical-message"></p>
    <button id="clinical-back">Back</button>
  `;
  return section;
}

export async function initClinical() {
  document.getElementById('clinical-back').onclick = () => window.loadFeature('patients');

  document.getElementById('clinical-save').onclick = async () => {
    const patient_id = document.getElementById('clinical-patient-id').value.trim();
    const symptoms = document.getElementById('clinical-symptoms').value.trim();
    const risk_factors = document.getElementById('clinical-risk-factors').value.trim();
    const age = document.getElementById('clinical-age').value;
    const sex = document.getElementById('clinical-sex').value;
    const smoker = document.getElementById('clinical-smoker').checked;
    const hiv_positive = document.getElementById('clinical-hiv').checked;
    const msg = document.getElementById('clinical-message');

    if (!patient_id || !symptoms || !age || !sex) {
      msg.textContent = 'Patient ID, symptoms, age, and sex are required.';
      return;
    }

    const payload = {
      patient_id,
      symptoms: symptoms.split(',').map(s => s.trim()).filter(Boolean),
      risk_factors: risk_factors.split(',').map(r => r.trim()).filter(Boolean),
      age: Number(age),
      sex,
      smoker,
      hiv_positive,
    };

    if (!navigator.onLine) {
      enqueueOfflineAction('clinical/', 'POST', payload);
      msg.textContent = 'Offline: clinical data queued for sync.';
      return;
    }

    const token = localStorage.getItem('accessToken');
    try {
      const resp = await fetch(`${API_BASE}clinical/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (resp.ok) {
        msg.textContent = 'Clinical data saved successfully.';
      } else {
        enqueueOfflineAction('clinical/', 'POST', payload);
        msg.textContent = data.detail || 'Failed to save clinical data; queued for retry.';
      }
    } catch (error) {
      console.error(error);
      enqueueOfflineAction('clinical/', 'POST', payload);
      msg.textContent = 'Network error saving clinical data; queued for retry.';
    }
  };
}
