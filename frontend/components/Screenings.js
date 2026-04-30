import { useState } from 'react';
import {
  createClinicalData,
  createFeedback,
  createLab,
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

const splitList = (value) => value.split(',').map((item) => item.trim()).filter(Boolean);

function ResultCard({ result }) {
  if (!result) return null;

  const score = Number(result.tb_score || 0);
  const riskClass = score >= 80 ? 'riskHigh' : score >= 50 ? 'riskMedium' : 'riskLow';

  return (
    <section className={`panel aiResult ${riskClass}`}>
      <div>
        <p className="eyebrow">{result.input_modality || 'AI'} result</p>
        <h3>{score}% TB score</h3>
        <p>{result.triage_recommendation}</p>
      </div>
      <div className="scoreGrid">
        <span>Image probability <strong>{result.image_prob ?? 'N/A'}</strong></span>
        <span>Tabular probability <strong>{result.tabular_prob ?? 'N/A'}</strong></span>
        <span>Model source <strong>{result.model_source || 'backend'}</strong></span>
      </div>
    </section>
  );
}

export default function Screenings({ setCurrentFeature }) {
  const [patientId, setPatientId] = useState('');
  const [screeningId, setScreeningId] = useState('');
  const [imageId, setImageId] = useState('');
  const [labId, setLabId] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('M');
  const [imagePath, setImagePath] = useState('');
  const [symptoms, setSymptoms] = useState('cough, fever');
  const [riskFactors, setRiskFactors] = useState('tb contact');
  const [smoker, setSmoker] = useState(false);
  const [hivPositive, setHivPositive] = useState(false);
  const [labForm, setLabForm] = useState({ genexpert: 'pending', smear: 'pending', culture: 'pending' });
  const [aiResult, setAiResult] = useState(null);
  const [output, setOutput] = useState(null);
  const [message, setMessage] = useState('');

  async function run(label, action, useAiResult = false) {
    setMessage(`${label}...`);
    try {
      const data = await action();
      if (useAiResult) setAiResult(data);
      setOutput(data);
      setMessage(`${label} complete.`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  function inferencePayload(includeImage) {
    return {
      patient_id: Number(patientId),
      image_path: includeImage && imagePath ? imagePath : undefined,
      age: age ? Number(age) : undefined,
      sex,
    };
  }

  const clinicalPayload = () => ({
    patient_id: Number(patientId),
    symptoms: splitList(symptoms),
    risk_factors: splitList(riskFactors),
    age: Number(age),
    sex,
    smoker,
    hiv_positive: hivPositive,
  });

  return (
    <main>
      <div className="topbar">
        <div>
          <h2>AI TB Workbench</h2>
          <p className="muted">Run CXR, tabular, or fusion inference using the MediVision AI pipeline.</p>
        </div>
        <button onClick={() => setCurrentFeature('patients')}>Back</button>
      </div>

      <section className="panel">
        <h3>Patient and Modalities</h3>
        <div className="inline">
          <input value={patientId} onChange={(event) => setPatientId(event.target.value)} placeholder="Patient ID" />
          <input type="number" value={age} onChange={(event) => setAge(event.target.value)} placeholder="Age" />
          <select value={sex} onChange={(event) => setSex(event.target.value)}>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>
        <input value={imagePath} onChange={(event) => setImagePath(event.target.value)} placeholder="Server-side CXR image path, optional" />
        <p className="muted">Use age and sex for tabular XGBoost. Add an image path for CNN or fusion inference.</p>
      </section>

      <section className="grid">
        <div className="panel">
          <h3>Inference</h3>
          <button onClick={() => run('Tabular inference', () => runInference(inferencePayload(false)), true)}>Run Tabular</button>
          <button onClick={() => run('Image inference', () => runInference({ patient_id: Number(patientId), image_path: imagePath }), true)}>Run Image</button>
          <button onClick={() => run('Fusion inference', () => runInference(inferencePayload(true)), true)}>Run Fusion</button>
        </div>

        <div className="panel">
          <h3>Clinical Features</h3>
          <input value={symptoms} onChange={(event) => setSymptoms(event.target.value)} placeholder="Symptoms, comma separated" />
          <input value={riskFactors} onChange={(event) => setRiskFactors(event.target.value)} placeholder="Risk factors, comma separated" />
          <label className="check">
            <input type="checkbox" checked={smoker} onChange={(event) => setSmoker(event.target.checked)} />
            Smoker
          </label>
          <label className="check">
            <input type="checkbox" checked={hivPositive} onChange={(event) => setHivPositive(event.target.checked)} />
            HIV positive
          </label>
          <button onClick={() => run('Save clinical data', () => createClinicalData(clinicalPayload()))}>Save Clinical Data</button>
        </div>

        <div className="panel">
          <h3>Lab Evidence</h3>
          <input value={labForm.genexpert} onChange={(event) => setLabForm({ ...labForm, genexpert: event.target.value })} placeholder="GeneXpert result" />
          <input value={labForm.smear} onChange={(event) => setLabForm({ ...labForm, smear: event.target.value })} placeholder="Smear microscopy" />
          <input value={labForm.culture} onChange={(event) => setLabForm({ ...labForm, culture: event.target.value })} placeholder="Culture result" />
          <button onClick={() => run('Create lab', () => createLab({ patient_id: Number(patientId), ...labForm }))}>Create Lab</button>
          <button onClick={() => run('Load labs', () => getLabsByPatient(patientId))}>Labs By Patient</button>
          <div className="inline">
            <input value={labId} onChange={(event) => setLabId(event.target.value)} placeholder="Lab ID" />
            <button onClick={() => run('Update lab', () => updateLab(labId, labForm))}>Update</button>
          </div>
        </div>

        <div className="panel">
          <h3>AI Artifacts</h3>
          <button onClick={() => run('Upload image metadata', () => uploadImage({ patient_id: Number(patientId), image_path: imagePath }))}>Upload Image Metadata</button>
          <div className="inline">
            <input value={imageId} onChange={(event) => setImageId(event.target.value)} placeholder="Image ID" />
            <button onClick={() => run('Get image', () => getImage(imageId))}>Get</button>
            <button onClick={() => run('Delete image', () => deleteImage(imageId))}>Delete</button>
          </div>
          <div className="inline">
            <input value={screeningId} onChange={(event) => setScreeningId(event.target.value)} placeholder="Screening ID" />
            <button onClick={() => run('Get screening', () => getScreening(screeningId))}>Screening</button>
            <button onClick={() => run('Report', () => getReport(screeningId))}>Report</button>
          </div>
          <button onClick={() => run('Screenings by patient', () => getScreeningsByPatient(patientId))}>Screenings By Patient</button>
          <button onClick={() => run('Create feedback', () => createFeedback({ screening_id: screeningId, note: 'Reviewed from AI workbench' }))}>Create Feedback</button>
        </div>
      </section>

      <ResultCard result={aiResult} />
      {message && <p className="message">{message}</p>}
      {output && <pre className="panel">{JSON.stringify(output, null, 2)}</pre>}
    </main>
  );
}
