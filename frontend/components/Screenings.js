import { useState } from 'react';
import {
  createClinicalData,
  createFeedback,
  createLab,
  createScreening,
  deleteImage,
  getImage,
  getLabsByPatient,
  getReport,
  getScreening,
  getScreeningsByPatient,
  runInference,
  updateLab,
  uploadImage,
} from '../lib/api';

export default function Screenings({ setCurrentFeature }) {
  const [patientId, setPatientId] = useState('');
  const [screeningId, setScreeningId] = useState('');
  const [imageId, setImageId] = useState('');
  const [labId, setLabId] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('M');
  const [output, setOutput] = useState(null);
  const [message, setMessage] = useState('');

  async function run(label, action) {
    setMessage(`${label}...`);
    try {
      const data = await action();
      setOutput(data);
      setMessage(`${label} complete.`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  const clinicalPayload = () => ({
    patient_id: Number(patientId),
    symptoms: ['cough', 'fever'],
    risk_factors: ['contact'],
    age: Number(age),
    sex,
    smoker: false,
    hiv_positive: false,
  });

  return (
    <main>
      <div className="topbar">
        <div>
          <h2>Diagnostics</h2>
          <p className="muted">Clinical, imaging, labs, screenings, inference, reports, and feedback.</p>
        </div>
        <button onClick={() => setCurrentFeature('patients')}>Back</button>
      </div>

      <section className="panel">
        <div className="inline">
          <input value={patientId} onChange={(event) => setPatientId(event.target.value)} placeholder="Patient ID" />
          <input value={screeningId} onChange={(event) => setScreeningId(event.target.value)} placeholder="Screening ID" />
          <input value={imageId} onChange={(event) => setImageId(event.target.value)} placeholder="Image ID" />
          <input value={labId} onChange={(event) => setLabId(event.target.value)} placeholder="Lab ID" />
        </div>
        <div className="inline">
          <input type="number" value={age} onChange={(event) => setAge(event.target.value)} placeholder="Age" />
          <select value={sex} onChange={(event) => setSex(event.target.value)}>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>
      </section>

      <section className="grid">
        <div className="panel">
          <h3>Clinical and Imaging</h3>
          <button onClick={() => run('Save clinical data', () => createClinicalData(clinicalPayload()))}>Save Clinical Data</button>
          <button onClick={() => run('Upload image metadata', () => uploadImage({ patient_id: Number(patientId), image_path: 'manual-ui-upload' }))}>Upload Image</button>
          <button onClick={() => run('Get image', () => getImage(imageId))}>Get Image</button>
          <button onClick={() => run('Delete image', () => deleteImage(imageId))}>Delete Image</button>
        </div>

        <div className="panel">
          <h3>Labs</h3>
          <button onClick={() => run('Create lab', () => createLab({ patient_id: Number(patientId), genexpert: 'pending', smear: 'pending', culture: 'pending' }))}>Create Lab</button>
          <button onClick={() => run('Load labs', () => getLabsByPatient(patientId))}>Labs By Patient</button>
          <button onClick={() => run('Update lab', () => updateLab(labId, { status: 'reviewed' }))}>Update Lab</button>
        </div>

        <div className="panel">
          <h3>Screening and Inference</h3>
          <button onClick={() => run('Create screening', () => createScreening({ patient_id: Number(patientId) }))}>Create Screening</button>
          <button onClick={() => run('Run inference', () => runInference({ patient_id: Number(patientId), age: Number(age), sex }))}>Run Inference</button>
          <button onClick={() => run('Get screening', () => getScreening(screeningId))}>Get Screening</button>
          <button onClick={() => run('Screenings by patient', () => getScreeningsByPatient(patientId))}>Screenings By Patient</button>
        </div>

        <div className="panel">
          <h3>Reports and Feedback</h3>
          <button onClick={() => run('Load report', () => getReport(screeningId))}>Load Report</button>
          <button onClick={() => run('Create feedback', () => createFeedback({ screening_id: screeningId, note: 'Reviewed in frontend console' }))}>Create Feedback</button>
        </div>
      </section>

      {message && <p className="message">{message}</p>}
      {output && <pre className="panel">{JSON.stringify(output, null, 2)}</pre>}
    </main>
  );
}
