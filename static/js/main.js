/**
 * Energy Anomaly Detection System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(message => {
                const alert = bootstrap.Alert.getOrCreateInstance(message);
                alert.close();
            });
        }, 5000);
    }
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('fade-in');
    });
    
    // Format numbers with comma separators
    const formatNumbers = document.querySelectorAll('.format-number');
    formatNumbers.forEach(element => {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = value.toLocaleString();
        }
    });
    
    // Handle sidebar expansion/collapse
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
            
            // Save state in localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar_collapsed', isCollapsed);
        });
        
        // Check stored state
        const storedState = localStorage.getItem('sidebar_collapsed');
        if (storedState === 'true') {
            document.getElementById('sidebar').classList.add('collapsed');
        }
    }
    
    // Handle theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const body = document.body;
            const isDark = body.classList.contains('dark-theme');
            
            if (isDark) {
                body.classList.remove('dark-theme');
                body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
                
                // Update toggle icon
                const icon = themeToggle.querySelector('i');
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            } else {
                body.classList.remove('light-theme');
                body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
                
                // Update toggle icon
                const icon = themeToggle.querySelector('i');
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
        });
        
        // Check stored theme
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme === 'light') {
            themeToggle.click(); // Switch to light theme
        }
    }
    
    // File input customization
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'No file chosen';
            const label = input.nextElementSibling;
            if (label && label.classList.contains('custom-file-label')) {
                label.textContent = fileName;
            }
        });
    });
    
    // Form validation 
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Handle confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = button.dataset.confirm || 'Are you sure you want to proceed?';
            
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
    
    // Handle range inputs with linked number inputs
    const rangeInputs = document.querySelectorAll('input[type="range"][data-linked-input]');
    rangeInputs.forEach(range => {
        const linkedInputId = range.dataset.linkedInput;
        const linkedInput = document.getElementById(linkedInputId);
        
        if (linkedInput) {
            // Update number input when range changes
            range.addEventListener('input', function() {
                linkedInput.value = range.value;
            });
            
            // Update range when number input changes
            linkedInput.addEventListener('input', function() {
                range.value = linkedInput.value;
            });
        }
    });
});