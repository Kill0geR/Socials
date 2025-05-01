document.addEventListener('DOMContentLoaded', function () {
    const burgerMenu = document.getElementById('burger-menu');
    const dropdownContent = document.querySelector('.dropdown-content');
    const burgerIcon = document.getElementById('burger-icon');
    const mobileMenu = document.getElementById('mobile-menu');

    burgerMenu?.addEventListener('click', () => {
        burgerMenu.classList.toggle('change');
        if (burgerMenu.classList.contains('change')) {
            burgerMenu.innerHTML = '&#9587;';
        } else {
            burgerMenu.innerHTML = 'Platforms';
        }
        dropdownContent.classList.toggle('show');
    });


    document.addEventListener('click', (e) => {
        if (!burgerMenu.contains(e.target) && !dropdownContent.contains(e.target)) {
            burgerMenu.classList.remove('change');
            burgerMenu.innerHTML = 'Platforms';
            dropdownContent.classList.remove('show');
        }
    });

    burgerIcon?.addEventListener('click', () => {
        mobileMenu.classList.toggle('show');
        burgerIcon.innerHTML = mobileMenu.classList.contains('show') ? '&#9587;' : '&#9776;';
    });

    document.addEventListener('click', (e) => {
        if (!burgerIcon.contains(e.target) && !mobileMenu.contains(e.target)) {
            mobileMenu.classList.remove('show');
            burgerIcon.innerHTML = '&#9776;';
        }
    });
});
