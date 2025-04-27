document.getElementById('logout-btn').addEventListener('click', function(event) {
    event.preventDefault(); 
    
    const confirmLogout = confirm("Are you sure you want to log out?");
    
    if (confirmLogout) {
        window.location.href = event.target.href; 
    }
});

document.getElementById('delete-btn').addEventListener('click', function(e) {
    e.preventDefault(); 
    const confirmation = confirm('Are you sure you want to delete your account? This action cannot be undone.');
    if (confirmation) {
        document.getElementById('delete-account-form').submit(); 
    }
});
