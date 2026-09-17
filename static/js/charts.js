document.addEventListener('DOMContentLoaded', () => {
    initAdminCharts();
    initStudentCharts();
});

// Admin Dashboard Analytics Charts
async function initAdminCharts() {
    const adminCanvas = document.getElementById('applicationsByCompanyChart');
    if (!adminCanvas) return; // Not on admin page

    try {
        const response = await fetch('/api/admin/chart-data');
        if (!response.ok) return;
        const data = await response.json();

        // 1. Applications by Company (Bar Chart)
        new Chart(adminCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: data.applications_by_company.labels,
                datasets: [{
                    label: 'Total Applications',
                    data: data.applications_by_company.data,
                    backgroundColor: 'rgba(79, 70, 229, 0.85)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });

        // 2. Placement Status (Doughnut Chart)
        const placementStatusCanvas = document.getElementById('placementStatusChart');
        if (placementStatusCanvas) {
            new Chart(placementStatusCanvas.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.placement_status.labels,
                    datasets: [{
                        data: data.placement_status.data,
                        backgroundColor: ['#10b981', '#64748b', '#f59e0b'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    },
                    cutout: '65%'
                }
            });
        }

        // 3. Department-wise Placements (Stacked Bar Chart)
        const deptCanvas = document.getElementById('deptPlacementsChart');
        if (deptCanvas) {
            new Chart(deptCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.dept_placements.labels,
                    datasets: [
                        {
                            label: 'Placed',
                            data: data.dept_placements.placed,
                            backgroundColor: '#10b981',
                            borderRadius: 4
                        },
                        {
                            label: 'Unplaced',
                            data: data.dept_placements.unplaced,
                            backgroundColor: '#e2e8f0',
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
                    },
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

        // 4. Monthly Application Trends (Line Chart)
        const trendsCanvas = document.getElementById('applicationTrendsChart');
        if (trendsCanvas) {
            new Chart(trendsCanvas.getContext('2d'), {
                type: 'line',
                data: {
                    labels: data.application_trends.labels,
                    datasets: [{
                        label: 'Applications',
                        data: data.application_trends.data,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#4f46e5',
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    }
                }
            });
        }

        // 5. Salary Distribution (Bar Chart)
        const salaryCanvas = document.getElementById('salaryDistributionChart');
        if (salaryCanvas) {
            new Chart(salaryCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.salary_distribution.labels,
                    datasets: [{
                        label: 'Job Postings',
                        data: data.salary_distribution.data,
                        backgroundColor: [
                            '#94a3b8',
                            '#06b6d4',
                            '#4f46e5',
                            '#10b981',
                            '#f59e0b'
                        ],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    }
                }
            });
        }

    } catch (e) {
        console.error('Error loading admin chart analytics:', e);
    }
}

// Student Dashboard Application Chart
function initStudentCharts() {
    const studentStatusCanvas = document.getElementById('studentAppStatusChart');
    if (!studentStatusCanvas) return;

    try {
        const labels = JSON.parse(studentStatusCanvas.getAttribute('data-labels') || '[]');
        const values = JSON.parse(studentStatusCanvas.getAttribute('data-values') || '[]');

        // Check if all zero
        const total = values.reduce((a, b) => a + b, 0);

        new Chart(studentStatusCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: total > 0 ? labels : ['No Applications Yet'],
                datasets: [{
                    data: total > 0 ? values : [1],
                    backgroundColor: total > 0 ? [
                        '#64748b', // Applied
                        '#06b6d4', // Under Review
                        '#4f46e5', // Shortlisted
                        '#f59e0b', // Interview
                        '#10b981', // Selected
                        '#ef4444'  // Rejected
                    ] : ['#e2e8f0'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                cutout: '70%'
            }
        });
    } catch (e) {
        console.error('Error rendering student chart:', e);
    }
}
