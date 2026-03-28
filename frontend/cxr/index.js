const API_BASE = 'http://127.0.0.1:8000/api/';  
export function cxrUI() {  
  const section = document.createElement('section');  
  section.innerHTML = `  
    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">CXR Upload + Analysis</h2>  
    <label style="color: #34495e; font-weight: bold;">Patient ID:</label><br>
    <input id="cxr-patient-id" placeholder="Enter Patient ID" style="margin-bottom: 10px; padding: 8px; width: 200px;" /><br>  
    
    <label style="color: #34495e; font-weight: bold;">CXR File:</label><br>
    <input id="cxr-file" type="file" accept="image/png, image/jpeg, image/dicom" style="margin-bottom: 10px;" /><br>  
    
    <label style="color: #34495e; font-weight: bold;">Position:</label><br>
    <select id="cxr-position" style="margin-bottom: 10px; padding: 5px;">
      <option value="standing">Standing</option>
      <option value="supine">Supine</option>
    </select><br>
    
    <label style="color: #34495e; font-weight: bold;">View:</label><br>
    <select id="cxr-view" style="margin-bottom: 15px; padding: 5px;">
      <option value="PA">PA</option>
      <option value="AP">AP</option>
    </select><br>
    
    <button id="cxr-submit" style="background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Upload & Analyze</button>  
    <button id="cxr-back" style="background-color: #95a5a6; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">Back</button><br>
    
    <p id="cxr-message" style="color: #e74c3c; margin-top: 15px;"></p>  
    <pre id="cxr-result" style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6;"></pre>  
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
      message.style.color = '#e74c3c';
      return;  
    }  
    
    const formData = new FormData();  
    formData.append('patient_id', patient_id);  
    formData.append('view', document.getElementById('cxr-view').value);  
    formData.append('position', document.getElementById('cxr-position').value);  
    formData.append('file', fileInput.files[0]);  
    
    message.textContent = 'Uploading...';  
    message.style.color = '#3498db';
    
    try {  
      const resp = await fetch(`${API_BASE}cxr/upload/`, {  
        method: 'POST',  
        headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },  
        body: formData,  
      });  
      const data = await resp.json();  
      if (resp.ok) {  
        message.textContent = '✓ Upload complete';  
        message.style.color = '#27ae60';
        result.textContent = JSON.stringify(data, null, 2);  
      } else {  
        message.textContent = data.detail || 'CXR upload failed';  
        message.style.color = '#e74c3c';
      }  
    } catch (error) {  
      console.error(error);  
      message.textContent = 'Network error uploading CXR';  
      message.style.color = '#e74c3c';
    }  
  };  
}