/**
 * Post item form - file upload preview.
 */
(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        var input = document.getElementById('imageUpload');
        var fileName = document.getElementById('fileName');
        if (input && fileName) {
            input.addEventListener('change', function () {
                if (this.files.length === 0) {
                    fileName.textContent = 'No files chosen';
                } else if (this.files.length === 1) {
                    fileName.textContent = this.files[0].name;
                } else {
                    fileName.textContent = this.files.length + ' files selected';
                }
            });
        }
    });
})();
