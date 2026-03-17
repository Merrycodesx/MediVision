const API_BASE = 'http://127.0.0.1:8000/api/';

function register() {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    fetch(`${API_BASE}auth/register/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (response.ok) {
            document.getElementById('register-message').textContent = 'Registration successful! Please login.';
            // Optionally redirect to login after a delay
            setTimeout(() => {
                window.location.href = '../index.html';
            }, 2000);
        } else {
            document.getElementById('register-message').textContent = 'Registration failed: ' + JSON.stringify(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('register-message').textContent = 'Error registering';
    });
}