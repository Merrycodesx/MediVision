const API_BASE = 'http://127.0.0.1:8000/api/';  
export function cxrUI() {  
  const section = document.createElement('section');  
  section.innerHTML = `  
    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">CXR Upload + Analysis</h2>  
    <label style="color: #34495e; font-weight: bold;">Patient ID:</label><br>
    <input id="cxr-patient-id" placeholder="Enter Patient ID" style="margin-bottom: 10px; padding: 8px; width: 200px;" /><br>  
    
    <label style="color: #34495e; font-weight: bold;">Age:</label><br>
    <input id="cxr-age" type="number" placeholder="Patient Age" style="margin-bottom: 10px; padding: 8px; width: 200px;" /><br>
    
    <label style="color: #34495e; font-weight: bold;">Sex:</label><br>
    <select id="cxr-sex" style="margin-bottom: 15px; padding: 5px;">
      <option value="M">Male</option>
      <option value="F">Female</option>
    </select><br>
    
    <button id="cxr-submit" style="background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Run AI Inference</button>  
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
    const age = document.getElementById('cxr-age').value;
    const sex = document.getElementById('cxr-sex').value;
    const message = document.getElementById('cxr-message');  
    const result = document.getElementById('cxr-result');  
    
    if (!patient_id || !age) {  
      message.textContent = 'Patient ID and Age are required.';  
      message.style.color = '#e74c3c';
      return;  
    }  
    
    message.textContent = 'Running AI inference...';  
    message.style.color = '#3498db';
    
    try {  
      const resp = await fetch(`${API_BASE}inference/run/`, {  
        method: 'POST',  
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}` 
        },  
        body: JSON.stringify({ patient_id, age: parseInt(age), sex }),  
      });  
      const data = await resp.json();  
      if (resp.ok && data.success) {  
        message.textContent = '✓ Inference complete';  
        message.style.color = '#27ae60';
        result.textContent = JSON.stringify(data, null, 2);  
      } else {  
        message.textContent = data.message || 'Inference failed';  
        message.style.color = '#e74c3c';
      }  
    } catch (error) {  
      console.error(error);  
      message.textContent = 'Network error running inference';  
      message.style.color = '#e74c3c';
    }  
  };  
}