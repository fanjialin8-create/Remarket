/**
 * Confirm dialog for destructive actions - replaces inline onclick.
 * Use: <a href="..." class="js-confirm" data-confirm="Message">Link</a>
 */
(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('a.js-confirm').forEach(function (el) {
            el.addEventListener('click', function (e) {
                var msg = el.getAttribute('data-confirm') || 'Are you sure?';
                if (!confirm(msg)) {
                    e.preventDefault();
                }
            });
        });
    });
})();
