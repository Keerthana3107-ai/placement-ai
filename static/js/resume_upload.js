document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('resumeDropZone');
    const fileInput = document.getElementById('resumeFileInput');
    const fileNameDisplay = document.getElementById('resumeFileNameDisplay');
    const uploadBtn = document.getElementById('resumeUploadSubmitBtn');

    if (!dropZone || !fileInput) return;

    // Drag-and-drop events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('border-primary', 'bg-light');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('border-primary', 'bg-light');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('Please select a valid PDF file.');
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            alert('File size exceeds the 16MB limit.');
            return;
        }

        if (fileNameDisplay) {
            fileNameDisplay.innerHTML = `
                <div class="alert alert-info py-2 d-flex align-items-center justify-content-between mb-0">
                    <div>
                        <i class="bi bi-file-earmark-pdf-fill text-danger fs-5 me-2"></i>
                        <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)
                    </div>
                    <span class="badge bg-success">Ready to Upload & Analyze</span>
                </div>
            `;
        }

        if (uploadBtn) {
            uploadBtn.disabled = false;
        }
    }
});
