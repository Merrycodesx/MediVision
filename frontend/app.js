const API_BASE = 'http://127.0.0.1:8000/api/';
let accessToken = null;
let refreshToken = null;
let selectedPatientId = null;
let currentUser = null;

function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    fetch(`${API_BASE}auth/token/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, role }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            accessToken = data.access;
            refreshToken = data.refresh;
            currentUser = {
                id: data.user_id,
                role: data.role,
                hospital_id: data.hospital_id,
                hospital_name: data.hospital_name
            };
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('main-section').style.display = 'block';
            document.getElementById('auth-message').textContent = '';
            document.getElementById('user-info').textContent = `Logged in as ${data.role} at ${data.hospital_name}`;
            loadPatients();
        } else {
            document.getElementById('auth-message').textContent = data.message || 'Login failed';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('auth-message').textContent = 'Error logging in';
    });
}

function loadPatients() {
    fetch(`${API_BASE}patients/`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.results) {
            const list = document.getElementById('patients-list');
            list.innerHTML = '';
            data.results.forEach(patient => {
                const li = document.createElement('li');
                li.textContent = `${patient.full_name}, Age: ${patient.age}`;

                const detailsButton = document.createElement('button');
                detailsButton.textContent = 'Details';
                detailsButton.style.marginLeft = '10px';
                detailsButton.onclick = () => showPatientDetails(patient);

                const screenButton = document.createElement('button');
                screenButton.textContent = 'Screen';
                screenButton.style.marginLeft = '10px';
                screenButton.onclick = () => screenPatient(patient);

                li.appendChild(detailsButton);
                li.appendChild(screenButton);
                list.appendChild(li);
            });
        } else {
            console.error('Failed to load patients:', data);
        }

        hidePatientDetails();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function showPatientDetails(patient) {
    selectedPatientId = patient.id;
    document.getElementById('detail-name').value = patient.full_name;
    document.getElementById('detail-age').value = patient.age;
    document.getElementById('patient-detail-section').style.display = 'block';
    document.getElementById('patient-detail-message').textContent = '';
}

function updatePatient() {
    if (!selectedPatientId) {
        document.getElementById('patient-detail-message').textContent = 'Select a patient first';
        return;
    }

    const full_name = document.getElementById('detail-name').value;
    const age = document.getElementById('detail-age').value;

    fetch(`${API_BASE}patients/${selectedPatientId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ full_name, age: parseInt(age) }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('patient-detail-message').textContent = 'Patient updated';
            loadPatients();
        } else {
            document.getElementById('patient-detail-message').textContent = data.message || 'Failed to update patient';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('patient-detail-message').textContent = 'Error updating patient';
    });
}

function deletePatient() {
    if (!selectedPatientId) {
        document.getElementById('patient-detail-message').textContent = 'Select a patient first';
        return;
    }

    fetch(`${API_BASE}patients/${selectedPatientId}/`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('patient-detail-message').textContent = 'Patient deleted';
            loadPatients();
        } else {
            return response.json().then(data => {
                document.getElementById('patient-detail-message').textContent = data.message || 'Failed to delete patient';
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('patient-detail-message').textContent = 'Error deleting patient';
    });
}

function addPatient() {
    const full_name = document.getElementById('patient-name').value;
    const age = document.getElementById('patient-age').value;

    fetch(`${API_BASE}patients/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ full_name, age: parseInt(age) }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('patient-message').textContent = 'Patient added';
            loadPatients();
        } else {
            document.getElementById('patient-message').textContent = data.message || 'Failed to add patient';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('patient-message').textContent = 'Error adding patient';
    });
}

function screenPatient(patient) {
    // Run AI inference for the patient
    fetch(`${API_BASE}inference/run/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
            patient_id: patient.id,
            age: patient.age,
            sex: patient.sex || 'unknown'
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Screening completed!\nTB Score: ${data.tb_score}%\nRecommendation: ${data.triage_recommendation}`);
            loadPatients(); // Refresh to show updated screenings
        } else {
            alert('Screening failed: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error running screening');
    });
}