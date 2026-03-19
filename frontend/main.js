import { initAuth, authUI } from './auth/index.js';
import { registerUI, initRegister } from './registration/index.js';
import { userManagementUI, initUserManagement } from './user-management/index.js';
import { patientsUI, initPatients } from './patients/index.js';
import { cxrUI, initCXR } from './cxr/index.js';
import { labUI, initLab } from './lab/index.js';
import { fusionUI, initFusion } from './fusion/index.js';
import { reportingUI, initReporting } from './reporting/index.js';
import { initOffline } from './offline/index.js';

const featureMap = {
  auth: { render: authUI, init: initAuth },
  register: { render: registerUI, init: initRegister },
  userManagement: { render: userManagementUI, init: initUserManagement },
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
