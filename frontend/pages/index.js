import { useState } from 'react';
import Auth from '../components/Auth';
import Register from '../components/Register';
import Patients from '../components/Patients';
import UserManagement from '../components/UserManagement';
import AdminPanel from '../components/AdminPanel';
import Screenings from '../components/Screenings';
import Offline from '../components/Offline';
import Footer from '../components/Footer';
import AppHeader from '../components/AppHeader';
import { useUI } from '../lib/ui-context';

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
  const [currentFeature, setCurrentFeature] = useState('landing');
  const [history, setHistory] = useState([]);
  const { t, fontFamily, fontSize } = useUI();

  const navigateTo = (feature) => {
    setHistory((prev) => (prev[prev.length - 1] === currentFeature ? prev : [...prev, currentFeature]));
    setCurrentFeature(feature);
  };

  const goBack = () => {
    setHistory((prev) => {
      if (!prev.length) return prev;
      const next = [...prev];
      const last = next.pop();
      setCurrentFeature(last);
      return next;
    });
  };

  const CurrentComponent = featureMap[currentFeature];
  const isAuthScreen = currentFeature === 'auth';
  const isLanding = currentFeature === 'landing';

  return (
    <div className={`container${isLanding ? ' landingContainer' : ''}`} style={{ fontFamily, fontSize: `${fontSize}px` }}>
      <AppHeader
        canGoBack={!isLanding && history.length > 0}
        onBack={goBack}
        transparent={isLanding || currentFeature === 'register'}
        variant={isLanding ? 'onImage' : 'default'}
      />
      {!isAuthScreen && !isLanding && <h1>MediVision Multimodal TB CAD</h1>}
      <div id="feature-container">
        {isLanding ? (
          <section className="landingHero" role="banner" aria-label="MediVision landing page">
            <div className="landingHeroMedia" aria-hidden="true">
              <img
                src="/landing-bg.png"
                alt=""
                className="landingHeroBg"
              />
            </div>
            <div className="landingOverlay">
              <h1>{t('app_title', 'MediVision Multimodal TB CAD')}</h1>
              <p>{t('app_subtitle', 'AI-powered Tuberculosis Diagnosis System')}</p>
              <div className="landingActions btnGroup">
                <button type="button" className="btn btn--primary" onClick={() => navigateTo('auth')}>{t('login', 'Login')}</button>
                <button type="button" className="btn btn--primary" onClick={() => navigateTo('register')}>{t('registration', 'Registration')}</button>
              </div>
            </div>
          </section>
        ) : (
          <CurrentComponent setCurrentFeature={navigateTo} />
        )}
      </div>
      <Footer version="v1.0.0" lastUpdated="May 2026" copyrightOwner="MediVision" />
      <Offline />
    </div>
  );
}
