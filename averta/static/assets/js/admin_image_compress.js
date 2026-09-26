/**
 * Admin image compression — runs in the browser (WebP when supported, else JPEG).
 * Does not use server RAM.
 */
(function () {
    'use strict';

    function getJQuery() {
        if (typeof django !== 'undefined' && django.jQuery) {
            return django.jQuery;
        }
        if (typeof jQuery !== 'undefined') {
            return jQuery;
        }
        if (
            typeof window.$ !== 'undefined' &&
            typeof window.$.fn !== 'undefined' &&
            typeof window.$.fn.jquery !== 'undefined'
        ) {
            return window.$;
        }
        return null;
    }

    function supportsWebPEncode() {
        try {
            var canvas = document.createElement('canvas');
            canvas.width = 1;
            canvas.height = 1;
            return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
        } catch (e) {
            return false;
        }
    }

    /** Raster image by MIME type or extension; skip video and SVG (not suitable for canvas). */
    function fileLooksLikeRasterImage(file) {
        if (!file) return false;
        if (file.type && /^video\//.test(file.type)) return false;
        if (file.type === 'image/svg+xml') return false;
        var base = (file.name || '').toLowerCase();
        if (/\.svg$/i.test(base)) return false;

        if (file.type && /^image\//.test(file.type)) return true;

        return /\.(jpe?g|png|gif|webp|bmp|avif|heic|heif)$/i.test(base);
    }

    var jqAttempts = 0;
    var MAX_JQ_ATTEMPTS = 250;

    function startScript() {
        var $ = getJQuery();

        if (!$) {
            jqAttempts += 1;
            if (jqAttempts > MAX_JQ_ATTEMPTS) {
                console.error(
                    '[Image Compress] jQuery not found — admin media may be missing or script ran too early.'
                );
                return;
            }
            setTimeout(startScript, 100);
            return;
        }

        (function ($) {
            var USE_WEBP_OUTPUT = supportsWebPEncode();
            if (!USE_WEBP_OUTPUT) {
                console.warn('[Image Compress] WebP encode unavailable — using JPEG output.');
            } else {
                console.log('[Image Compress] Output: WebP with JPEG fallback when needed.');
            }

            console.log('[Image Compress] jQuery:', $.fn.jquery);

            function compressImageSmart(file, maxWidth, maxHeight, quality, preferWebp) {
                return new Promise(function (resolve, reject) {
                    var reader = new FileReader();

                    reader.onload = function (e) {
                        var img = new Image();

                        img.onload = function () {
                            var canvas = document.createElement('canvas');
                            var width = img.width;
                            var height = img.height;

                            if (width > maxWidth || height > maxHeight) {
                                var ratio = Math.min(maxWidth / width, maxHeight / height);
                                width = width * ratio;
                                height = height * ratio;
                            }

                            canvas.width = width;
                            canvas.height = height;

                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0, width, height);

                            var nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');

                            function packFile(blob, mime, ext) {
                                var compressedFile = new File([blob], nameWithoutExt + ext, {
                                    type: mime,
                                    lastModified: Date.now(),
                                });
                                resolve(compressedFile);
                            }

                            function tryJpeg() {
                                canvas.toBlob(function (blobJ) {
                                    if (!blobJ) {
                                        reject(new Error('JPEG conversion failed'));
                                        return;
                                    }
                                    packFile(blobJ, 'image/jpeg', '.jpg');
                                }, 'image/jpeg', quality);
                            }

                            if (preferWebp) {
                                canvas.toBlob(function (blobW) {
                                    if (blobW) {
                                        packFile(blobW, 'image/webp', '.webp');
                                    } else {
                                        tryJpeg();
                                    }
                                }, 'image/webp', quality);
                            } else {
                                tryJpeg();
                            }
                        };

                        img.onerror = function () {
                            reject(new Error('Image loading failed'));
                        };

                        img.src = e.target.result;
                    };

                    reader.onerror = function () {
                        reject(new Error('File reading failed'));
                    };

                    reader.readAsDataURL(file);
                });
            }

            function handleImageCompression(e) {
                var el = e.target;
                if (!el || el.tagName !== 'INPUT' || el.type !== 'file') {
                    return;
                }

                var $input = $(el);

                if ($input.data('compress-ignore-next-change')) {
                    $input.data('compress-ignore-next-change', false);
                    return;
                }

                var inputName = $input.attr('name') || '';
                var inputId = $input.attr('id') || '';

                if ($input.data('compression-processing')) {
                    return;
                }

                var files = el.files;

                if (!files || files.length === 0) {
                    $input.data('compression-processing', false);
                    return;
                }

                var imageFiles = [];
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];

                    if (!fileLooksLikeRasterImage(file)) {
                        continue;
                    }

                    if (USE_WEBP_OUTPUT && file.type === 'image/webp') {
                        console.log('[Image Compress] Already WebP, skip:', file.name);
                        continue;
                    }

                    imageFiles.push(file);
                }

                if (imageFiles.length === 0) {
                    $input.data('compression-processing', false);
                    return;
                }

                $input.data('compression-processing', true);

                console.log('[Image Compress] Selected:', imageFiles.length, 'image(s) —', inputName || inputId || 'file input');

                var $progress = $input.siblings('.compress-progress');
                if ($progress.length === 0) {
                    $progress = $(
                        '<div class="compress-progress" style="margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 4px; border: 1px solid #2196f3;">' +
                            '<div style="font-weight: bold; margin-bottom: 5px; color: #1976d2;">Compressing images…</div>' +
                            '<div class="compress-info" style="font-size: 12px; color: #666;"></div>' +
                            '<div class="compress-status" style="font-size: 11px; color: #666; margin-top: 5px;"></div>' +
                            '</div>'
                    );
                    $input.after($progress);
                }

                $progress.show();
                var totalOriginalSize = 0;
                imageFiles.forEach(function (file) {
                    totalOriginalSize += file.size;
                });
                $progress
                    .find('.compress-info')
                    .text(
                        'Selected ' +
                            imageFiles.length +
                            ' image(s). Original size: ' +
                            (totalOriginalSize / 1024).toFixed(2) +
                            ' KB'
                    );
                $progress.find('.compress-status').text('Please wait…');

                var compressPromises = imageFiles.map(function (file, index) {
                    return compressImageSmart(file, 1920, 1080, 0.8, USE_WEBP_OUTPUT)
                        .then(function (compressedFile) {
                            return { success: true, file: compressedFile, originalFile: file, index: index };
                        })
                        .catch(function (error) {
                            console.error('[Image Compress]', file.name, error);
                            return { success: false, error: error, originalFile: file, index: index };
                        });
                });

                Promise.all(compressPromises)
                    .then(function (results) {
                        var compressedFiles = [];
                        var failedFiles = [];

                        results.forEach(function (result) {
                            if (result.success) {
                                compressedFiles.push(result);
                            } else {
                                failedFiles.push(result);
                            }
                        });

                        var dataTransfer = new DataTransfer();

                        for (var j = 0; j < files.length; j++) {
                            var file = files[j];
                            if (!fileLooksLikeRasterImage(file)) {
                                dataTransfer.items.add(file);
                                continue;
                            }
                            var passThrough = USE_WEBP_OUTPUT && file.type === 'image/webp';
                            if (passThrough) {
                                dataTransfer.items.add(file);
                            }
                        }

                        failedFiles.forEach(function (result) {
                            dataTransfer.items.add(result.originalFile);
                            console.log('[Image Compress] Kept original:', result.originalFile.name);
                        });

                        compressedFiles.forEach(function (result) {
                            dataTransfer.items.add(result.file);
                            console.log('[Image Compress] Done:', result.file.name, (result.file.size / 1024).toFixed(2) + ' KB');
                        });

                        var nativeInput = $input[0];
                        $input.data('compress-ignore-next-change', true);
                        nativeInput.files = dataTransfer.files;
                        setTimeout(function () {
                            $input.data('compress-ignore-next-change', false);
                        }, 100);

                        $input.data('compression-processing', false);

                        var totalCompressedSize = 0;
                        compressedFiles.forEach(function (result) {
                            totalCompressedSize += result.file.size;
                        });

                        var totalSaved =
                            compressedFiles.length > 0 ? ((1 - totalCompressedSize / totalOriginalSize) * 100).toFixed(1) : '0';
                        var totalSavedKB = ((totalOriginalSize - totalCompressedSize) / 1024).toFixed(2);

                        var statusText = '';
                        if (compressedFiles.length > 0) {
                            statusText += compressedFiles.length + ' image(s) compressed:<br>';
                            compressedFiles.forEach(function (result) {
                                var originalSize = (result.originalFile.size / 1024).toFixed(2);
                                var compressedSize = (result.file.size / 1024).toFixed(2);
                                var saved = ((1 - result.file.size / result.originalFile.size) * 100).toFixed(1);
                                statusText +=
                                    'OK ' +
                                    result.file.name +
                                    ': ' +
                                    originalSize +
                                    ' KB → ' +
                                    compressedSize +
                                    ' KB (' +
                                    saved +
                                    '% smaller)<br>';
                            });
                        }

                        if (failedFiles.length > 0) {
                            statusText +=
                                '<br>' + failedFiles.length + ' not compressed (using original):<br>';
                            failedFiles.forEach(function (result) {
                                statusText += 'WARN ' + result.originalFile.name + '<br>';
                            });
                        }

                        var infoText = '';
                        if (compressedFiles.length === imageFiles.length) {
                            infoText = '<strong>All images compressed.</strong><br>';
                        } else if (compressedFiles.length > 0) {
                            infoText =
                                '<strong>' +
                                compressedFiles.length +
                                ' compressed, ' +
                                failedFiles.length +
                                ' failed.</strong><br>';
                        } else {
                            infoText = '<strong>Could not compress any image.</strong><br>';
                        }

                        if (compressedFiles.length > 0) {
                            infoText +=
                                'Total: ' +
                                (totalOriginalSize / 1024).toFixed(2) +
                                ' KB → ' +
                                (totalCompressedSize / 1024).toFixed(2) +
                                ' KB<br>' +
                                'Saved: ' +
                                totalSaved +
                                '% (' +
                                totalSavedKB +
                                ' KB)';
                        }

                        $progress.find('.compress-info').html(infoText);
                        $progress.find('.compress-status').html(statusText);

                        if (compressedFiles.length === imageFiles.length) {
                            $progress.css({
                                background: '#e8f5e9',
                                'border-color': '#4caf50',
                            });
                        } else if (compressedFiles.length > 0) {
                            $progress.css({
                                background: '#fff3e0',
                                'border-color': '#ff9800',
                            });
                        } else {
                            $progress.css({
                                background: '#ffebee',
                                'border-color': '#f44336',
                            });
                        }

                        setTimeout(function () {
                            $progress.fadeOut();
                        }, 8000);
                    })
                    .catch(function (error) {
                        console.error('[Image Compress]', error);
                        $input.data('compression-processing', false);
                        $progress
                            .find('.compress-info')
                            .html(
                                '<strong>Error:</strong> ' + error.message + '<br>Original files will be used.'
                            );
                        $progress.find('.compress-status').text('');
                        $progress.css({
                            background: '#ffebee',
                            'border-color': '#f44336',
                        });
                        setTimeout(function () {
                            $progress.fadeOut();
                        }, 5000);
                    });
            }

            function initImageCompression() {
                $('input[type="file"]').each(function () {
                    var $input = $(this);
                    if ($input.data('compression-initialized')) {
                        return;
                    }
                    $input.data('compression-initialized', true);
                });
                console.log('[Image Compress] Watching file inputs:', $('input[type="file"]').length);
            }

            $(document).on('change', 'input[type="file"]', handleImageCompression);

            function setupMutationObserver() {
                if (typeof MutationObserver === 'undefined') {
                    console.warn('[Image Compress] MutationObserver not supported');
                    return;
                }

                var observer = new MutationObserver(function (mutations) {
                    var foundNewInputs = false;
                    mutations.forEach(function (mutation) {
                        mutation.addedNodes.forEach(function (node) {
                            if (node.nodeType === 1) {
                                var $node = $(node);
                                var $inputs = $node.find('input[type="file"]').add($node.filter('input[type="file"]'));
                                if ($inputs.length > 0) {
                                    foundNewInputs = true;
                                }
                            }
                        });
                    });

                    if (foundNewInputs) {
                        setTimeout(initImageCompression, 100);
                    }
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                });

                console.log('[Image Compress] MutationObserver active');
            }

            $(document).ready(function () {
                console.log('[Image Compress] Script ready');
                setTimeout(initImageCompression, 300);
                setupMutationObserver();

                $(document).on('formset:added', function () {
                    setTimeout(initImageCompression, 200);
                });
            });
        })($);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startScript);
    } else {
        startScript();
    }
})();
