const API_BASE = 'http://127.0.0.1:8000/api/';
let accessToken = null;
let selectedPatientId = null;

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch(`${API_BASE}auth/token/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            accessToken = data.access;
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('main-section').style.display = 'block';
            document.getElementById('auth-message').textContent = '';
        } else {
            document.getElementById('auth-message').textContent = 'Login failed';
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
        const list = document.getElementById('patients-list');
        list.innerHTML = '';
        data.forEach(patient => {
            const li = document.createElement('li');
            li.textContent = `${patient.name}, Age: ${patient.age}`;

            const detailsButton = document.createElement('button');
            detailsButton.textContent = 'Details';
            detailsButton.style.marginLeft = '10px';
            detailsButton.onclick = () => showPatientDetails(patient);

            li.appendChild(detailsButton);
            list.appendChild(li);
        });

        hidePatientDetails();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function showPatientDetails(patient) {
    selectedPatientId = patient.id;
    document.getElementById('detail-name').value = patient.name;
    document.getElementById('detail-age').value = patient.age;
    document.getElementById('patient-detail-section').style.display = 'block';
    document.getElementById('patient-detail-message').textContent = '';
}

function hidePatientDetails() {
    selectedPatientId = null;
    document.getElementById('patient-detail-section').style.display = 'none';
    document.getElementById('patient-detail-message').textContent = '';
}

function updatePatient() {
    if (!selectedPatientId) {
        document.getElementById('patient-detail-message').textContent = 'Select a patient first';
        return;
    }

    const name = document.getElementById('detail-name').value;
    const age = document.getElementById('detail-age').value;

    fetch(`${API_BASE}patients/${selectedPatientId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ name, age: parseInt(age) }),
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('patient-detail-message').textContent = 'Patient updated';
            loadPatients();
        } else {
            document.getElementById('patient-detail-message').textContent = 'Failed to update patient';
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
            document.getElementById('patient-detail-message').textContent = 'Failed to delete patient';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('patient-detail-message').textContent = 'Error deleting patient';
    });
}

function addPatient() {
    const name = document.getElementById('patient-name').value;
    const age = document.getElementById('patient-age').value;

    fetch(`${API_BASE}patients/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ name, age: parseInt(age) }),
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('patient-message').textContent = 'Patient added';
            loadPatients();
        } else {
            document.getElementById('patient-message').textContent = 'Failed to add patient';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('patient-message').textContent = 'Error adding patient';
    });
}