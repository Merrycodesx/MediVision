import { initAuth, authUI } from './features/auth/index.js';
import { patientsUI, initPatients } from './features/patients/index.js';
import { cxrUI, initCXR } from './features/cxr/index.js';
import { labUI, initLab } from './features/lab/index.js';
import { fusionUI, initFusion } from './features/fusion/index.js';
import { reportingUI, initReporting } from './features/reporting/index.js';
import { initOffline } from './features/offline/index.js';

const featureMap = {
  auth: { render: authUI, init: initAuth },
  patients: { render: patientsUI, init: initPatients },
  cxr: { render: cxrUI, init: initCXR },
  lab: { render: labUI, init: initLab },
  fusion: { render: fusionUI, init: initFusion },
  reporting: { render: reportingUI, init: initReporting },
};

window.loadFeature = async (feature) => {
  const container = document.getElementById('feature-container');
  container.innerHTML = '';
  if (!featureMap[feature]) return;
  container.appendChild(featureMap[feature].render());
  await featureMap[feature].init();
};

window.addEventListener('load', async () => {
  initOffline();
  await loadFeature('auth');
});
