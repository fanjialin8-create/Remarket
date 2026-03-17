/**
 * Order status update via AJAX - no page reload.
 * Implements front-end interactivity requirement for ITECH.
 */
(function () {
    'use strict';

    document.querySelectorAll('.order-status-select').forEach(function (select) {
        select.addEventListener('change', function () {
            var form = this.closest('form');
            var url = form.action;
            var csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;
            var status = this.value;
            var statusDisplay = form.closest('.dashboard-order-row').querySelector('.order-status-display');
            var originalValue = this.dataset.originalValue;

            if (status === originalValue) return;

            var fd = new FormData();
            fd.append('csrfmiddlewaretoken', csrf);
            fd.append('status', status);

            fetch(url, {
                method: 'POST',
                body: fd,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin'
            })
                .then(function (res) {
                    if (!res.ok) throw new Error('Request failed');
                    return res.json();
                })
                .then(function (data) {
                    if (data.success && statusDisplay) {
                        statusDisplay.textContent = data.status;
                        select.dataset.originalValue = data.status;
                    } else if (!data.success) {
                        select.value = originalValue;
                    }
                })
                .catch(function () {
                    select.value = originalValue;
                });
        });
    });
})();
