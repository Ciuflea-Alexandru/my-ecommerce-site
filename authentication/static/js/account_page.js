function chooseFile() {
    document.getElementById("profile-picture-input").click();
}

function submitForm() {
    document.getElementById("profile-picture-form").submit();
}

function resetPassword() {
    window.location.reload();

    localStorage.setItem('changePasswordVisible', 'false');
}

function showContainer(containerId) {
    var containers = document.querySelectorAll('.Information-Container');
    containers.forEach(function(container) {
        if (container.id === containerId) {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    });

    if (containerId === 'change-password-container') {
        localStorage.setItem('changePasswordVisible', 'true');
    } else {
        localStorage.setItem('changePasswordVisible', 'false');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const changePasswordVisible = localStorage.getItem('changePasswordVisible');
    const initialContainer = localStorage.getItem('initialContainer');

    if (changePasswordVisible === 'true') {
        showContainer('change-password-container');
    } else if (initialContainer === 'personal-container') {
        showContainer('personal-container');
    } else {
        showContainer('account-container');
    }

    const buttons = document.querySelectorAll('.Main-Button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            buttons.forEach(btn => {
                btn.classList.remove('active');
            });

            this.classList.add('active');

            const containerId = this.dataset.container;
            localStorage.setItem('initialContainer', containerId);
        });
    });
});
