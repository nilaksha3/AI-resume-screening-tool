// Function to get CSRF Token (defined once)
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return '';
}

// Login form handler
document.addEventListener('DOMContentLoaded', function() {
    // Get login form elements if they exist
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const loginButton = document.getElementById('loginButton');
        const alert = document.getElementById('alert'); // Assuming there's an alert element

        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();  // Stop default form submission

            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            const selectedRole = document.querySelector('input[name="role"]:checked').value;

            if (!email || !password) {
                if (alert) {
                    alert.textContent = "Please enter both email and password.";
                    alert.classList.add('show');
                } else {
                    window.alert("Please enter both email and password.");
                }
                return;
            }

            loginButton.classList.add('loading');
            loginButton.disabled = true;

            try {
                // Send data to Django backend
                const response = await fetch('/api/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ 
                        email: email, 
                        password: password,
                        role: selectedRole  // Include role parameter
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('isLoggedIn', 'true');
                    localStorage.setItem('userRole', selectedRole);

                    if (alert) {
                        alert.textContent = "Login successful!";
                        alert.classList.add('show');
                    } else {
                        window.alert("Login successful!");
                    }

                    setTimeout(() => {
                        window.location.href = selectedRole === 'hr-manager' ? 'hrmanager.html' : 'candidate.html';
                    }, 1000);
                } else {
                    if (alert) {
                        alert.textContent = data.error || "Invalid login credentials.";
                        alert.classList.add('show');
                    } else {
                        window.alert(data.error || "Invalid login credentials.");
                    }
                }
            } catch (error) {
                console.error("Login error:", error);
                if (alert) {
                    alert.textContent = "Server error. Please try again later.";
                    alert.classList.add('show');
                } else {
                    window.alert("Server error. Please try again later.");
                }
            } finally {
                loginButton.classList.remove('loading');
                loginButton.disabled = false;
            }
        });
    }

    // Get signup form elements if they exist
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        const signupButton = document.getElementById('signupButton');
        const alert = document.getElementById('alert'); // Assuming there's an alert element

        signupForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            // Get form data
            const fullName = nameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            const confirmPassword = confirmPasswordInput.value.trim();
            const selectedRole = document.querySelector('input[name="role"]:checked').value;

            if (fullName === '' || email === '' || password === '' || confirmPassword === '') {
                if (alert) {
                    alert.textContent = "All fields are required.";
                    alert.classList.add('show');
                } else {
                    window.alert("All fields are required.");
                }
                return;
            }

            if (password !== confirmPassword) {
                if (alert) {
                    alert.textContent = "Passwords do not match.";
                    alert.classList.add('show');
                } else {
                    window.alert("Passwords do not match.");
                }
                return;
            }

            signupButton.classList.add('loading');
            signupButton.disabled = true;

            try {
                // Send data to Django backend
                const response = await fetch('/api/signup/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        email: email,
                        password: password,
                        role: selectedRole
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    if (alert) {
                        alert.textContent = "Account created successfully!";
                        alert.classList.add('show');
                    } else {
                        window.alert("Account created successfully!");
                    }
                    
                    localStorage.setItem('userRole', selectedRole);
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 1500);
                } else {
                    if (alert) {
                        alert.textContent = data.error || "Signup failed. Try again.";
                        alert.classList.add('show');
                    } else {
                        window.alert(data.error || "Signup failed. Try again.");
                    }
                }
            } catch (error) {
                console.error("Signup error:", error);
                if (alert) {
                    alert.textContent = "Server error. Please try again later.";
                    alert.classList.add('show');
                } else {
                    window.alert("Server error. Please try again later.");
                }
            } finally {
                signupButton.classList.remove('loading');
                signupButton.disabled = false;
            }
        });
    }
});