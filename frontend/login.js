// login.js

// Estado de la aplicación en memoria (no usar localStorage)
const appState = {
    token: null,
    user: null
};

const form = document.getElementById('loginForm');
const btnLogin = document.getElementById('btnLogin');
const alertBox = document.getElementById('alert');

// Función para mostrar alertas
function showAlert(message, type = 'error') {
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type}`;
    alertBox.style.display = 'block';
    
    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 5000);
}

// Manejo del formulario
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showAlert('Por favor complete todos los campos', 'error');
        return;
    }

    // Deshabilitar botón y mostrar loading
    btnLogin.disabled = true;
    btnLogin.innerHTML = 'Iniciando sesión<span class="loading"></span>';

    try {
        const response = await fetch('/api/auth/login', { 
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        const data = await response.json();

        if (response.ok) {
            // Guardar token en memoria
            appState.token = data.token;
            appState.user = username;

            // Guardar token y usuario en sessionStorage
            sessionStorage.setItem('token', data.token);
            sessionStorage.setItem('username', username);

            showAlert(`¡Bienvenido ${username}! Redirigiendo...`, 'success');

            // Redirigir a farmacia.html después de 2 segundos
            setTimeout(() => {
                window.location.href = 'farmacia.html';
            }, 2000);
        } else {
            showAlert(data.message || data.error || 'Credenciales inválidas', 'error');
        }
    } catch (err) {
        console.error('Error de conexión:', err);
        showAlert('Error al conectar con el servidor. Verifique que el backend esté ejecutándose en http://auth-service:5000', 'error');
    } finally {
        // Rehabilitar botón
        btnLogin.disabled = false;
        btnLogin.innerHTML = 'Iniciar Sesión';
    }
});
