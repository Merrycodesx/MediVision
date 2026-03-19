const API_BASE = 'http://127.0.0.1:8000/api/';

export function fusionUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Fusion & Risk Scoring</h2>
    <input id="fusion-patient-id" placeholder="Patient ID" /><br>
    <label>Low/Med/High thresholds (optional)</label><br>
    <input id="fusion-threshold-low" placeholder="Low threshold" type="number" step="1" min="0" max="100" /><br>
    <input id="fusion-threshold-med" placeholder="Medium threshold" type="number" step="1" min="0" max="100" /><br>
    <input id="fusion-threshold-high" placeholder="High threshold" type="number" step="1" min="0" max="100" /><br>
    <button id="fusion-run">Run Fusion</button>
    <p id="fusion-message"></p>
    <pre id="fusion-result"></pre>
    <button id="fusion-back">Back</button>
  `;
  return section;
}

export async function initFusion() {
  document.getElementById('fusion-back').onclick = () => window.loadFeature('patients');

  document.getElementById('fusion-run').onclick = async () => {
    const patientId = document.getElementById('fusion-patient-id').value;
    const msg = document.getElementById('fusion-message');
    const result = document.getElementById('fusion-result');

    if (!patientId) {
      msg.textContent = 'Patient ID required.';
      return;
    }

    const body = { 
      thresholds: {
        low: Number(document.getElementById('fusion-threshold-low').value || 40),
        medium: Number(document.getElementById('fusion-threshold-med').value || 70),
        high: Number(document.getElementById('fusion-threshold-high').value || 90),
      }
    };

    try {
      const resp = await fetch(`${API_BASE}fusion/${patientId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify(body),
      });
      const data = await resp.json();
      if (resp.ok) {
        msg.textContent = 'Fusion completed';
        result.textContent = JSON.stringify(data, null, 2);
      } else {
        msg.textContent = data.detail || 'Fusion failed';
      }
    } catch (error) {
      console.error(error);
      msg.textContent = 'Network error running fusion';
    }
  };
}
