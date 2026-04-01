const API_BASE = 'http://127.0.0.1:8000/api/';

export function reportingUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Reporting</h2>
    <input id="report-patient-id" placeholder="Patient ID" /><br>
    <button id="report-load">Load Report</button>
    <button id="report-export">Export (PDF/JSON/HL7-FHIR)</button>
    <p id="report-message"></p>
    <pre id="report-content"></pre>
    <button id="report-back">Back</button>
  `;
  return section;
}

export async function initReporting() {
  document.getElementById('report-back').onclick = () => window.loadFeature('patients');

  document.getElementById('report-load').onclick = async () => {
    const patientId = document.getElementById('report-patient-id').value;
    const msg = document.getElementById('report-message');
    const out = document.getElementById('report-content');

    if (!patientId) {
      msg.textContent = 'Patient ID required';
      return;
    }

    try {
      const resp = await fetch(`${API_BASE}reports/${patientId}/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      const data = await resp.json();
      if (resp.ok) {
        out.textContent = JSON.stringify(data, null, 2);
        msg.textContent = 'Report loaded';
      } else {
        msg.textContent = data.detail || 'Failed to load report';
      }
    } catch (error) {
      console.error(error);
      msg.textContent = 'Network error';
    }
  };

  document.getElementById('report-export').onclick = () => {
    document.getElementById('report-message').textContent = 'Export support is a placeholder in this UI.';
  };
}
