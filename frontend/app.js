const API_BASE = 'http://127.0.0.1:8000/api/';
let accessToken = null;

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
            list.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Error:', error);
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