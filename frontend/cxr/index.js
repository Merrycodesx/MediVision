const API_BASE = 'http://127.0.0.1:8000/api/';

export function cxrUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>CXR Upload + Analysis</h2>
    <input id="cxr-patient-id" placeholder="Patient ID" /><br>
    <input id="cxr-file" type="file" accept="image/png, image/jpeg, image/dicom" /><br>
    <select id="cxr-view"><option value="PA">PA</option><option value="AP">AP</option></select>
    <select id="cxr-position"><option value="standing">Standing</option><option value="supine">Supine</option></select><br>
    <button id="cxr-submit">Upload & Analyze</button>
    <p id="cxr-message"></p>
    <pre id="cxr-result"></pre>
    <button id="cxr-back">Back</button>
  `;
  return section;
}

export async function initCXR() {
  document.getElementById('cxr-back').onclick = () => window.loadFeature('patients');
  document.getElementById('cxr-submit').onclick = async () => {
    const patient_id = document.getElementById('cxr-patient-id').value;
    const fileInput = document.getElementById('cxr-file');
    const message = document.getElementById('cxr-message');
    const result = document.getElementById('cxr-result');

    if (!patient_id || !fileInput.files.length) {
      message.textContent = 'Patient ID and CXR file are required.';
      return;
    }

    const formData = new FormData();
    formData.append('patient_id', patient_id);
    formData.append('view', document.getElementById('cxr-view').value);
    formData.append('position', document.getElementById('cxr-position').value);
    formData.append('file', fileInput.files[0]);

    message.textContent = 'Uploading...';

    try {
      const resp = await fetch(`${API_BASE}cxr/upload/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        body: formData,
      });
      const data = await resp.json();
      if (resp.ok) {
        message.textContent = 'Upload complete';
        result.textContent = JSON.stringify(data, null, 2);
      } else {
        message.textContent = data.detail || 'CXR upload failed';
      }
    } catch (error) {
      console.error(error);
      message.textContent = 'Network error uploading CXR';
    }
  };
}
