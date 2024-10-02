// Function to handle user signup
async function signup(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    const response = await fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    alert(data.detail || 'Signup successful! You can now log in.');
}

// Function to handle user login
async function login(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ username: email, password }),
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token); // Store the access token
        window.location.href = 'dashboard.html'; // Redirect to dashboard
    } else {
        const error = await response.json();
        alert(error.detail);
    }
}

// Function to handle document upload
async function uploadDocument(event) {
    event.preventDefault();

    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/upload', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token'), // Include token
        },
        body: formData,
    });

    const data = await response.json();
    alert(data.detail || 'File uploaded successfully!');
}

// Function to ask a question
async function askQuestion(event) {
    event.preventDefault();

    const question = document.getElementById('question').value;

    const response = await fetch('/ask?question=' + encodeURIComponent(question), {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token'), // Include token
        },
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById('output').innerText = data.response || 'No answer found.';
    } else {
        const error = await response.json();
        alert(error.detail || 'An error occurred.');
    }
}

// Add event listeners to forms and buttons
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const uploadForm = document.getElementById('upload-form');
    const askButton = document.getElementById('ask-button');

    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }

    if (signupForm) {
        signupForm.addEventListener('submit', signup);
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', uploadDocument);
    }

    if (askButton) {
        askButton.addEventListener('click', askQuestion);
    }
});
