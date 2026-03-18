/**
 * Order status update via AJAX - no page reload.
 * Poll to sync when buyer confirms/reports (seller sees update).
 */
(function () {
    'use strict';

    var POLL_INTERVAL_MS = 15000;
    var el = document.querySelector('[data-sold-orders-api-url]');
    if (el) {
        var apiUrl = el.dataset.soldOrdersApiUrl;
        function pollStatuses() {
            fetch(apiUrl, {
                method: 'GET',
                headers: { 'Accept': 'application/json' },
                credentials: 'same-origin'
            })
                .then(function (res) { return res.ok ? res.json() : null; })
                .then(function (data) {
                    if (!data || !data.orders) return;
                    data.orders.forEach(function (o) {
                        var card = document.querySelector('.order-card-clean[data-order-id="' + o.id + '"]');
                        if (!card) return;
                        if (o.status === 'Completed') {
                            var form = card.querySelector('.order-status-form');
                            if (form) {
                                var span = document.createElement('span');
                                span.className = 'order-status-badge';
                                span.textContent = 'Completed';
                                form.parentNode.insertBefore(span, form);
                                form.remove();
                            }
                        } else {
                            var select = card.querySelector('.order-status-select');
                            if (select && select.value !== o.status) {
                                select.value = o.status;
                                select.dataset.originalValue = o.status;
                            }
                        }
                    });
                })
                .catch(function () {});
        }
        setInterval(pollStatuses, POLL_INTERVAL_MS);
        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState === 'visible') pollStatuses();
        });
    }

    document.querySelectorAll('.order-status-select').forEach(function (select) {
        select.addEventListener('change', function () {
            var form = this.closest('form');
            var url = form.action;
            var csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;
            var status = this.value;
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
                    if (data.success) {
                        select.dataset.originalValue = data.status;
                    } else {
                        select.value = originalValue;
                    }
                })
                .catch(function () {
                    select.value = originalValue;
                });
        });
    });
})();
