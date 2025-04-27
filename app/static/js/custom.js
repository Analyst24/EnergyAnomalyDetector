/**
 * Energy Anomaly Detection System
 * Custom JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Toggle password visibility
    var togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var input = document.querySelector(button.getAttribute('data-target'));
            if (input.type === 'password') {
                input.type = 'text';
                button.innerHTML = '<i class="bi bi-eye-slash"></i>';
            } else {
                input.type = 'password';
                button.innerHTML = '<i class="bi bi-eye"></i>';
            }
        });
    });

    // Handle file input styling
    var fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = e.target.files[0].name;
            var label = e.target.nextElementSibling;
            label.innerHTML = fileName;
        });
    });

    // Add copy functionality to code snippets
    if (typeof ClipboardJS !== 'undefined') {
        var clipboard = new ClipboardJS('.copy-button');
        
        clipboard.on('success', function(e) {
            var originalText = e.trigger.innerHTML;
            e.trigger.innerHTML = '<i class="bi bi-check"></i> Copied!';
            
            setTimeout(function() {
                e.trigger.innerHTML = originalText;
            }, 2000);
            
            e.clearSelection();
        });
        
        clipboard.on('error', function(e) {
            var originalText = e.trigger.innerHTML;
            e.trigger.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Error!';
            
            setTimeout(function() {
                e.trigger.innerHTML = originalText;
            }, 2000);
        });
    }

    // Highlight active link in sidebar
    var currentLocation = window.location.pathname;
    var navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    // Confirm dialog for delete actions
    var confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // Dynamic form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});