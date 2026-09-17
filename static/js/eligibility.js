document.addEventListener('DOMContentLoaded', () => {
    // Attach listener to all quick eligibility check buttons
    document.querySelectorAll('.btn-check-eligibility').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const jobId = button.getAttribute('data-job-id');
            if (!jobId) return;

            const modalTitle = document.getElementById('eligibilityModalTitle');
            const modalBody = document.getElementById('eligibilityModalBody');
            const applyBtn = document.getElementById('eligibilityModalApplyBtn');

            if (!modalBody) return;

            // Loading state
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-2 text-muted">Evaluating academic criteria and profile compatibility...</p>
                </div>
            `;

            const modal = new bootstrap.Modal(document.getElementById('eligibilityModal'));
            modal.show();

            try {
                const response = await fetch(`/api/check-eligibility/${jobId}`);
                if (!response.ok) throw new Error('Evaluation failed');
                const data = await response.json();

                if (modalTitle) {
                    modalTitle.innerHTML = `Eligibility Check: <strong>${data.job_title}</strong> (${data.company_name})`;
                }

                let statusBadge = data.is_eligible
                    ? `<div class="alert alert-success d-flex align-items-center mb-3">
                         <i class="bi bi-check-circle-fill fs-4 me-2"></i>
                         <div>
                            <strong>Congratulations! You are eligible to apply for this role.</strong>
                         </div>
                       </div>`
                    : `<div class="alert alert-danger d-flex align-items-center mb-3">
                         <i class="bi bi-x-circle-fill fs-4 me-2"></i>
                         <div>
                            <strong>You do not meet one or more eligibility criteria.</strong>
                         </div>
                       </div>`;

                let reasonsHtml = '<div class="list-group list-group-flush mb-3">';

                // Passed criteria
                data.passed_reasons.forEach(r => {
                    reasonsHtml += `
                        <div class="list-group-item d-flex align-items-center text-success py-2">
                            <i class="bi bi-check2-circle fs-5 me-2 flex-shrink-0"></i>
                            <span>${r}</span>
                        </div>
                    `;
                });

                // Failed criteria
                data.failure_reasons.forEach(r => {
                    reasonsHtml += `
                        <div class="list-group-item d-flex align-items-center text-danger py-2">
                            <i class="bi bi-exclamation-octagon fs-5 me-2 flex-shrink-0"></i>
                            <span>${r}</span>
                        </div>
                    `;
                });
                reasonsHtml += '</div>';

                modalBody.innerHTML = `
                    ${statusBadge}
                    <h6 class="fw-bold mb-2">Criteria Breakdown:</h6>
                    ${reasonsHtml}
                `;

                if (applyBtn) {
                    if (data.is_eligible) {
                        applyBtn.style.display = 'inline-block';
                        applyBtn.onclick = () => {
                            // Submit application form
                            const form = document.createElement('form');
                            form.method = 'POST';
                            form.action = `/student/jobs/${jobId}/apply`;
                            document.body.appendChild(form);
                            form.submit();
                        };
                    } else {
                        applyBtn.style.display = 'none';
                    }
                }

            } catch (err) {
                modalBody.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Unable to fetch eligibility status. Please check your network or try again.
                    </div>
                `;
            }
        });
    });
});
