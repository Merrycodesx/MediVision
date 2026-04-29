import { useState } from 'react';
import {
  exportHms,
  getApiRoot,
  getAudits,
  getConfig,
  getFeedback,
  importHms,
  listModels,
  updateConfig,
  updateModels,
} from '../lib/api';

export default function AdminPanel({ setCurrentFeature }) {
  const [threshold, setThreshold] = useState('0.95');
  const [feedbackId, setFeedbackId] = useState('');
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

  return (
    <main>
      <div className="topbar">
        <div>
          <h2>Backend Tools</h2>
          <p className="muted">Configuration, audits, HMS integration, models, API root, and feedback review.</p>
        </div>
        <button onClick={() => setCurrentFeature('patients')}>Back</button>
      </div>

      <section className="grid">
        <div className="panel">
          <h3>Configuration</h3>
          <button onClick={() => run('Load API root', getApiRoot)}>API Root</button>
          <button onClick={() => run('Load config', getConfig)}>Get Config</button>
          <div className="inline">
            <input value={threshold} onChange={(event) => setThreshold(event.target.value)} placeholder="Sensitivity threshold" />
            <button onClick={() => run('Update config', () => updateConfig({ sensitivity_threshold: Number(threshold), other_params: {} }))}>Update</button>
          </div>
        </div>

        <div className="panel">
          <h3>Audit and Feedback</h3>
          <button onClick={() => run('Load audits', getAudits)}>Audits</button>
          <div className="inline">
            <input value={feedbackId} onChange={(event) => setFeedbackId(event.target.value)} placeholder="Feedback ID" />
            <button onClick={() => run('Get feedback', () => getFeedback(feedbackId))}>Get</button>
          </div>
        </div>

        <div className="panel">
          <h3>HMS Integration</h3>
          <button onClick={() => run('HMS import', () => importHms({ source: 'frontend', dry_run: true }))}>Import</button>
          <button onClick={() => run('HMS export', () => exportHms({ format: 'json' }))}>Export</button>
        </div>

        <div className="panel">
          <h3>Models</h3>
          <button onClick={() => run('List models', listModels)}>List Models</button>
          <button onClick={() => run('Update models', () => updateModels({ requested_by: 'frontend' }))}>Update Models</button>
        </div>
      </section>

      {message && <p className="message">{message}</p>}
      {output && <pre className="panel">{JSON.stringify(output, null, 2)}</pre>}
    </main>
  );
}
