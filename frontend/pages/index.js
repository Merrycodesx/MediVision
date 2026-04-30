import { useState } from 'react';
import Auth from '../components/Auth';
import Register from '../components/Register';
import Patients from '../components/Patients';
import UserManagement from '../components/UserManagement';
import AdminPanel from '../components/AdminPanel';
import Screenings from '../components/Screenings';
import Offline from '../components/Offline';

function Placeholder({ name, setCurrentFeature }) {
  return (
    <section>
      <h2>{name}</h2>
      <p>Feature not implemented yet.</p>
      <button onClick={() => setCurrentFeature('patients')}>Back</button>
    </section>
  );
}

const featureMap = {
  auth: Auth,
  register: Register,
  patients: Patients,
  userManagement: UserManagement,
  admin: AdminPanel,
  screenings: Screenings,
  cxr: Screenings,
  lab: Screenings,
  clinical: Screenings,
  fusion: Screenings,
  reporting: Screenings,
};

export default function Home() {
  const [currentFeature, setCurrentFeature] = useState('auth');

  const CurrentComponent = featureMap[currentFeature];

  return (
    <div className="container">
      <h1>MediVision Multimodal TB CAD</h1>
      <div id="feature-container">
        <CurrentComponent setCurrentFeature={setCurrentFeature} />
      </div>
      <Offline />
    </div>
  );
}
