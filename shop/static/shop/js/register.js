document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        

        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');

        let isValid = true;

        const username = document.getElementById('id_username');
        const firstName = document.getElementById('id_first_name');
        const lastName = document.getElementById('id_last_name');
        const email = document.getElementById('id_email');
        const phone = document.getElementById('id_phone');
        const password = document.getElementById('id_password');
        const confirmPassword = document.getElementById('id_confirm_password');

        if (!/^[A-Za-z0-9_]+$/.test(username.value)) {
            showError(username, 'Только латинские буквы, цифры и _');
            isValid = false;
        }

        if (!/^[A-ZА-ЯЁ][a-zа-яё-]+$/.test(firstName.value)) {
            showError(firstName, 'С заглавной буквы');
            isValid = false;
        }

        if (lastName.value && !/^[A-ZА-ЯЁ][a-zа-яё-]+$/.test(lastName.value)) {
            showError(lastName, 'С заглавной буквы');
            isValid = false;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
            showError(email, 'Неверный email');
            isValid = false;
        }

        if (!/^\+7\s?\(?[0-9]{3}\)?\s?[0-9]{3}-?[0-9]{2}-?[0-9]{2}$/.test(phone.value)) {
            showError(phone, 'Неверный формат');
            isValid = false;
        }

        if (password.value.length < 8) {
            showError(password, 'Минимум 8 символов');
            isValid = false;
        }

        if (password.value !== confirmPassword.value) {
            showError(confirmPassword, 'Пароли не совпадают');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    function showError(input, message) {
        const errorSpan = input.parentElement.querySelector('.error-message');
        if (errorSpan) errorSpan.textContent = message;
    }
});