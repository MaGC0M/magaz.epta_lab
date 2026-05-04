document.addEventListener('DOMContentLoaded', function () {
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackStatus = document.getElementById('feedback-status');
    const feedbackList = document.getElementById('feedback-list');

    if (!feedbackForm || !feedbackStatus || !feedbackList) {
        return;
    }

    const submitUrl = feedbackForm.dataset.submitUrl;
    const listUrl = feedbackForm.dataset.listUrl;

    function getCookie(name) {
        const cookieString = document.cookie;
        const cookies = cookieString.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }

        return null;
    }

    function escapeHtml(text) {
        return String(text || '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function renderFeedbacks(feedbacks) {
        if (!feedbacks || feedbacks.length === 0) {
            feedbackList.innerHTML = '<p id="no-feedbacks" class="no-feedbacks">Пока сообщений нет.</p>';
            return;
        }

        let html = '';

        feedbacks.forEach(function (feedback) {
            html += `
                <div class="feedback-item">
                    <div class="feedback-header">
                        <strong>${escapeHtml(feedback.name)}</strong>
                        <span class="feedback-date">${escapeHtml(feedback.created_at)}</span>
                    </div>
                    <p class="feedback-message">${escapeHtml(feedback.message)}</p>
                </div>
            `;
        });

        feedbackList.innerHTML = html;
    }

    async function loadFeedbacks() {
        try {
            const response = await fetch(listUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            });

            if (!response.ok) {
                console.error('Ошибка загрузки сообщений. Статус:', response.status);
                return;
            }

            const data = await response.json();
            renderFeedbacks(data.feedbacks || []);
        } catch (error) {
            console.error('Ошибка загрузки сообщений:', error);
        }
    }

    feedbackForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const payload = {
            name: document.getElementById('feedback-name').value.trim(),
            email: document.getElementById('feedback-email').value.trim(),
            message: document.getElementById('feedback-message').value.trim(),
        };

        try {
            const response = await fetch(submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            feedbackStatus.style.display = 'block';

            if (!response.ok) {
                feedbackStatus.textContent = data.message || 'Ошибка при отправке сообщения';
                return;
            }

            feedbackStatus.textContent = 'Сообщение отправлено без перезагрузки страницы.';
            document.getElementById('feedback-message').value = '';

            await loadFeedbacks();
        } catch (error) {
            feedbackStatus.style.display = 'block';
            feedbackStatus.textContent = 'Ошибка сети. Попробуйте ещё раз.';
            console.error('Ошибка отправки сообщения:', error);
        }
    });

    loadFeedbacks();

    setInterval(function () {
        loadFeedbacks();
    }, 3000);
});