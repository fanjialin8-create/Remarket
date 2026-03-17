/**
 * Chat AJAX polling - fetches new messages without page reload.
 * Implements front-end interactivity requirement for ITECH.
 */
(function () {
    'use strict';

    const container = document.getElementById('chatMessagesBox');
    if (!container) return;

    const currentUser = container.dataset.currentUser;
    const apiUrl = container.dataset.apiUrl;
    if (!apiUrl || !currentUser) return;
    const pollInterval = 3000; // 3 seconds
    let lastMessageId = getLastMessageId();

    function getLastMessageId() {
        const lastBubble = container.querySelector('.message-bubble:last-of-type');
        return lastBubble ? parseInt(lastBubble.dataset.messageId, 10) || 0 : 0;
    }

    function formatTime(isoStr) {
        const d = new Date(isoStr);
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const h = String(d.getHours()).padStart(2, '0');
        const min = String(d.getMinutes()).padStart(2, '0');
        return m + '-' + day + ' ' + h + ':' + min;
    }

    function renderMessage(msg) {
        const isOwn = msg.sender === currentUser;
        const rowClass = isOwn ? 'message-row message-row-own' : 'message-row';
        const bubbleClass = isOwn ? 'message-bubble message-bubble-own' : 'message-bubble';
        const time = formatTime(msg.created_at);

        const row = document.createElement('div');
        row.className = rowClass;
        row.innerHTML =
            '<div class="' + bubbleClass + '" data-message-id="' + msg.id + '">' +
            '<div class="message-meta">' +
            '<span class="message-sender">' + escapeHtml(msg.sender) + '</span>' +
            '<small class="message-time">' + escapeHtml(time) + '</small>' +
            '</div>' +
            '<p class="message-content mb-0">' + escapeHtml(msg.content) + '</p>' +
            '</div>';
        return row;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function appendNewMessages(messages) {
        let added = 0;
        for (let i = 0; i < messages.length; i++) {
            if (messages[i].id > lastMessageId) {
                container.appendChild(renderMessage(messages[i]));
                lastMessageId = messages[i].id;
                added++;
            }
        }
        if (added > 0) {
            container.scrollTop = container.scrollHeight;
            removeEmptyPlaceholder();
        }
    }

    function removeEmptyPlaceholder() {
        const placeholder = container.querySelector('.empty-mini-state');
        if (placeholder) placeholder.remove();
    }

    function poll() {
        fetch(apiUrl, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.messages) appendNewMessages(data.messages);
            })
            .catch(function () {});
    }

    // Initial last id from server-rendered messages
    lastMessageId = getLastMessageId();

    // Pause polling when tab hidden, resume when visible
    let intervalId = setInterval(poll, pollInterval);
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            clearInterval(intervalId);
        } else {
            intervalId = setInterval(poll, pollInterval);
        }
    });
})();
