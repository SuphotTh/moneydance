document.addEventListener('DOMContentLoaded', function() {
    // Check if it's a mobile device
    if ('ontouchstart' in document.documentElement) {
        document.querySelectorAll('.hover-dropdown').forEach(function(dropdown) {
            dropdown.addEventListener('click', function(e) {
                if (e.target.classList.contains('dropdown-toggle')) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.querySelector('.dropdown-menu').classList.toggle('show');
                }
            });
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function() {
            document.querySelectorAll('.dropdown-menu.show').forEach(function(dropdown) {
                dropdown.classList.remove('show');
            });
        });
    }
});