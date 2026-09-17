document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.app-sidebar');

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });

        // Close when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 992 && !sidebar.contains(e.target) && !sidebarToggleBtn.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }

    // 2. Notification System
    const notifBtn = document.getElementById('notifDropdownBtn');
    const markAllReadBtn = document.getElementById('markAllReadBtn');

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const res = await fetch('/api/notifications/mark-all-read', { method: 'POST' });
                if (res.ok) {
                    const badge = document.getElementById('notifBadge');
                    if (badge) badge.style.display = 'none';
                    document.querySelectorAll('.notif-item.unread').forEach(el => {
                        el.classList.remove('unread');
                    });
                }
            } catch (err) {
                console.error('Error marking notifications as read:', err);
            }
        });
    }

    // 3. Auto dismiss flash alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {}
        });
    }, 5000);

    // 4. Live Interview Countdown Timer
    initInterviewCountdown();
});

function initInterviewCountdown() {
    const timerElem = document.getElementById('interviewCountdown');
    if (!timerElem) return;

    const targetDateStr = timerElem.getAttribute('data-target-datetime');
    if (!targetDateStr) return;

    const targetDate = new Date(targetDateStr).getTime();

    function update() {
        const now = new Date().getTime();
        const diff = targetDate - now;

        if (diff <= 0) {
            timerElem.innerHTML = '<span class="text-success font-monospace">Interview In Progress / Scheduled Today!</span>';
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        const pad = (n) => String(n).padStart(2, '0');

        timerElem.innerHTML = `
            <div class="d-flex gap-3 justify-content-center">
                <div class="text-center"><span class="countdown-timer-digits">${pad(days)}</span><div class="small text-muted text-uppercase" style="font-size:0.7rem">Days</div></div>
                <div class="countdown-timer-digits">:</div>
                <div class="text-center"><span class="countdown-timer-digits">${pad(hours)}</span><div class="small text-muted text-uppercase" style="font-size:0.7rem">Hours</div></div>
                <div class="countdown-timer-digits">:</div>
                <div class="text-center"><span class="countdown-timer-digits">${pad(minutes)}</span><div class="small text-muted text-uppercase" style="font-size:0.7rem">Mins</div></div>
                <div class="countdown-timer-digits">:</div>
                <div class="text-center"><span class="countdown-timer-digits">${pad(seconds)}</span><div class="small text-muted text-uppercase" style="font-size:0.7rem">Secs</div></div>
            </div>
        `;
    }

    update();
    setInterval(update, 1000);
}
