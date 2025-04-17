// Chrome browser detection
document.addEventListener('DOMContentLoaded', function() {
    // Check if browser is Chrome
    function isChrome() {
        const userAgent = navigator.userAgent.toLowerCase();
        return userAgent.indexOf('chrome') > -1 && userAgent.indexOf('edge') === -1 && userAgent.indexOf('edg') === -1;
    }
    
    // If not Chrome, redirect to Chrome required page
    if (!isChrome()) {
        window.location.href = '/chrome_required';
    }
}); 