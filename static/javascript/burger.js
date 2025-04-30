document.addEventListener('DOMContentLoaded', function () {
    const burgerMenu = document.getElementById('burger-menu');
    const dropdownContent = document.querySelector('.dropdown-content');

    burgerMenu.addEventListener('click', () => {
        burgerMenu.classList.toggle('change');
        if (burgerMenu.classList.contains('change')) {
            burgerMenu.innerHTML = '&#9587;';
        } else {
            burgerMenu.innerHTML = 'Platform';
        }
        dropdownContent.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
        if (!burgerMenu.contains(e.target) && !dropdownContent.contains(e.target)) {
            burgerMenu.classList.remove('change');
            burgerMenu.innerHTML = 'Platform';
            dropdownContent.classList.remove('show');
        }
    });

});