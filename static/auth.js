async function submitForm(event, endpoint, redirectUrl) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const messageBox = form.querySelector('.message');
    const submitBtn = form.querySelector('button[type="submit"]');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            messageBox.textContent = result.message;
            messageBox.className = 'message success';
            messageBox.style.display = 'block';
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 1000);
        } else {
            messageBox.textContent = result.error || 'An error occurred';
            messageBox.className = 'message error';
            messageBox.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.textContent = 'Try Again';
        }
    } catch (error) {
        messageBox.textContent = 'Network error. Please try again.';
        messageBox.className = 'message error';
        messageBox.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Try Again';
    }
}

async function logout() {
    try {
        const response = await fetch('/api/auth/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (e) {
        console.error('Logout failed', e);
    }
}
