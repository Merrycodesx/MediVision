export function reportingUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Reporting</h2>
    <input id="report-patient-id" placeholder="Patient ID" />
    <button id="report-load">Load Report</button>
    <button id="report-export">Export PDF</button>
    <p id="report-message"></p>
    <pre id="report-content"></pre>
    <button id="report-back">Back</button>
  `;
  return section;
}

export async function initReporting() {
  document.getElementById('report-back').onclick = () => window.loadFeature('patients');

  document.getElementById('report-load').onclick = async () => {
    const id = document.getElementById('report-patient-id').value;
    const msg = document.getElementById('report-message');
    const display = document.getElementById('report-content');
    if (!id) {
      msg.textContent = 'Patient ID required';
      return;
    }

    try {
      const token = localStorage.getItem('accessToken');
      const resp = await fetch(`http://127.0.0.1:8000/api/reports/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await resp.json();
      if (resp.ok) {
        display.textContent = JSON.stringify(data, null, 2);
        msg.textContent = 'Report loaded';
      } else {
        msg.textContent = data.detail || 'Failed to load report';
      }
    } catch (e) {
      msg.textContent = 'Network error loading report';
      console.error(e);
    }
  };

  document.getElementById('report-export').onclick = () => {
    document.getElementById('report-message').textContent = 'Export features not implemented in scaffold.';
  };
}
