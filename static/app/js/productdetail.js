/**
 * Product detail image switching - click thumbnail to change main image.
 * Implements front-end interactivity requirement for ITECH.
 */
(function () {
    'use strict';

    const mainImg = document.getElementById('mainProductImage');
    const thumbs = document.querySelectorAll('.detail-thumb[data-src]');
    if (!mainImg || thumbs.length === 0) return;

    function switchTo(thumb) {
        const src = thumb.dataset.src;
        if (src) {
            mainImg.src = src;
            thumbs.forEach(function (t) { t.classList.remove('detail-thumb-active'); });
            thumb.classList.add('detail-thumb-active');
        }
    }

    thumbs.forEach(function (thumb) {
        thumb.addEventListener('click', function () { switchTo(this); });
        thumb.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                switchTo(this);
            }
        });
    });
})();
