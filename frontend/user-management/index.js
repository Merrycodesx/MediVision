const API_BASE = 'http://127.0.0.1:8000/api/';

export function userManagementUI() {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>User Management (Admin)</h2>
    <p>Use server API for user management; placeholder for feature completeness.</p>
    <button id="user-back">Back</button>
  `;
  return section;
}

export async function initUserManagement() {
  document.getElementById('user-back').onclick = () => window.loadFeature('patients');
}
