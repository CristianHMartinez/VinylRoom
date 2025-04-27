const signinButton = document.getElementById('signin');
const loginButton = document.getElementById('login');
const container = document.getElementById('container');

signinButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

loginButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});
