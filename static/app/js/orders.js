/**
 * Poll order statuses so buyer sees seller updates in real-time.
 * Handle buyer actions: Confirm received / Not received when status is Confirmed.
 */
(function () {
    'use strict';

    var POLL_INTERVAL_MS = 15000;
    var el = document.querySelector('[data-orders-api-url]');
    if (!el) return;
    var apiUrl = el.dataset.ordersApiUrl;
    if (!document.querySelector('.order-card-clean')) return;

    function getCsrfToken() {
        var csrf = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrf ? csrf.value : '';
    }

    function updateStatuses() {
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
                    var badge = card.querySelector('[data-order-status]');
                    var actions = card.querySelector('.buyer-actions');
                    if (badge && badge.textContent !== o.status) {
                        badge.textContent = o.status;
                    }
                    if (actions) {
                        actions.style.display = o.status === 'Confirmed' ? 'flex' : 'none';
                    }
                });
            })
            .catch(function () {});
    }

    document.querySelectorAll('[data-buyer-action]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var action = this.dataset.buyerAction;
            var actionsDiv = this.closest('.buyer-actions');
            if (!actionsDiv) return;
            var orderId = actionsDiv.dataset.orderId;
            var url = actionsDiv.dataset.actionUrl;
            if (!url || !action) return;
            var fd = new FormData();
            fd.append('csrfmiddlewaretoken', getCsrfToken());
            fd.append('action', action);
            btn.disabled = true;
            fetch(url, {
                method: 'POST',
                body: fd,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin'
            })
                .then(function (res) { return res.ok ? res.json() : null; })
                .then(function (data) {
                    if (data && data.success) {
                        var card = document.querySelector('.order-card-clean[data-order-id="' + orderId + '"]');
                        if (card) {
                            var badge = card.querySelector('[data-order-status]');
                            if (badge) badge.textContent = data.status;
                            if (actionsDiv) actionsDiv.style.display = 'none';
                        }
                    }
                })
                .catch(function () {})
                .finally(function () { btn.disabled = false; });
        });
    });

    var timer = setInterval(updateStatuses, POLL_INTERVAL_MS);
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') {
            updateStatuses();
        }
    });
})();
