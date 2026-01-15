document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const submitButton = e.target.querySelector('button[type="submit"]');

    // Disable button during upload
    submitButton.disabled = true;
    submitButton.textContent = 'Uploading...';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            // Show success message
            showAlert('success', result.message);

            // Reset form
            e.target.reset();

            // Reload page after 2 seconds to show new candidate
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert('error', result.error || 'Upload failed');
        }
    } catch (error) {
        showAlert('error', 'Network error. Please try again.');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Upload CV';
    }
});

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
