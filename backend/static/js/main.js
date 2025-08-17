// Main JavaScript file for Daily Scribbles CMS

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if( target.length ) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });

    // Search form enhancement
    $('#search-form').on('submit', function(e) {
        var searchInput = $(this).find('input[name="search"]');
        if (searchInput.val().trim() === '') {
            e.preventDefault();
            searchInput.focus();
            return false;
        }
    });

    // Character counter for textareas
    $('textarea[maxlength]').each(function() {
        var $this = $(this);
        var maxLength = $this.attr('maxlength');
        var $counter = $('<small class="form-text text-muted char-counter"></small>');
        $this.after($counter);
        
        function updateCounter() {
            var remaining = maxLength - $this.val().length;
            $counter.text(remaining + ' characters remaining');
            
            if (remaining < 20) {
                $counter.addClass('text-warning').removeClass('text-muted');
            } else {
                $counter.addClass('text-muted').removeClass('text-warning');
            }
        }
        
        updateCounter();
        $this.on('input', updateCounter);
    });

    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Form validation enhancement
    $('form').on('submit', function(e) {
        var $form = $(this);
        var isValid = true;

        // Check required fields
        $form.find('[required]').each(function() {
            var $field = $(this);
            if (!$field.val().trim()) {
                $field.addClass('is-invalid');
                isValid = false;
            } else {
                $field.removeClass('is-invalid').addClass('is-valid');
            }
        });

        // Email validation
        $form.find('input[type="email"]').each(function() {
            var $field = $(this);
            var email = $field.val();
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                $field.addClass('is-invalid');
                isValid = false;
            }
        });

        // Password confirmation
        var $password = $form.find('input[name="password1"]');
        var $confirmPassword = $form.find('input[name="password2"]');
        
        if ($password.length && $confirmPassword.length) {
            if ($password.val() !== $confirmPassword.val()) {
                $confirmPassword.addClass('is-invalid');
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
            $form.find('.is-invalid').first().focus();
        }
    });

    // Real-time field validation
    $('input, textarea').on('blur', function() {
        var $field = $(this);
        
        if ($field.attr('required') && !$field.val().trim()) {
            $field.addClass('is-invalid').removeClass('is-valid');
        } else if ($field.val().trim()) {
            $field.addClass('is-valid').removeClass('is-invalid');
        }
    });

    // Back to top button
    var $backToTop = $('<button class="btn btn-primary btn-sm position-fixed" style="bottom: 20px; right: 20px; z-index: 1000; display: none;"><i class="fas fa-arrow-up"></i></button>');
    $('body').append($backToTop);

    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $backToTop.fadeIn();
        } else {
            $backToTop.fadeOut();
        }
    });

    $backToTop.on('click', function() {
        $('html, body').animate({scrollTop: 0}, 600);
        return false;
    });

    // Reading progress bar
    if ($('.post-content').length) {
        var $progressBar = $('<div class="reading-progress position-fixed" style="top: 0; left: 0; width: 0%; height: 3px; background-color: #007bff; z-index: 1001; transition: width 0.3s;"></div>');
        $('body').prepend($progressBar);

        $(window).scroll(function() {
            var scrollTop = $(window).scrollTop();
            var docHeight = $(document).height();
            var winHeight = $(window).height();
            var scrollPercent = (scrollTop) / (docHeight - winHeight);
            var scrollPercentRounded = Math.round(scrollPercent * 100);
            
            $progressBar.css('width', scrollPercentRounded + '%');
        });
    }

    // Copy to clipboard functionality
    $('.copy-btn').on('click', function() {
        var text = $(this).data('copy');
        navigator.clipboard.writeText(text).then(function() {
            // Show success message
            var $btn = $('.copy-btn');
            var originalText = $btn.text();
            $btn.text('Copied!').addClass('btn-success').removeClass('btn-outline-secondary');
            
            setTimeout(function() {
                $btn.text(originalText).removeClass('btn-success').addClass('btn-outline-secondary');
            }, 2000);
        });
    });

    // Auto-resize textareas
    $('textarea').each(function() {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Keyboard shortcuts
    $(document).keydown(function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 75) {
            e.preventDefault();
            $('input[name="search"]').focus();
        }
        
        // Escape to close modals
        if (e.keyCode === 27) {
            $('.modal').modal('hide');
        }
    });
});

// Utility functions
function showLoading(element) {
    $(element).prop('disabled', true).html('<span class="loading"></span> Loading...');
}

function hideLoading(element, originalText) {
    $(element).prop('disabled', false).html(originalText);
}

function showNotification(message, type = 'info') {
    var alertClass = 'alert-' + type;
    var $alert = $('<div class="alert ' + alertClass + ' alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 1050; min-width: 300px;" role="alert">' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
        '</div>');
    
    $('body').append($alert);
    
    setTimeout(function() {
        $alert.fadeOut(function() {
            $(this).remove();
        });
    }, 5000);
}

// API helper functions
function apiCall(url, method = 'GET', data = null) {
    var options = {
        url: url,
        method: method,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    };

    if (method !== 'GET' && data) {
        options.data = JSON.stringify(data);
        options.headers['Content-Type'] = 'application/json';
        options.headers['X-CSRFToken'] = $('[name=csrfmiddlewaretoken]').val();
    }

    return $.ajax(options);
}

// Export functions for global use
window.DailyScribbles = {
    showLoading: showLoading,
    hideLoading: hideLoading,
    showNotification: showNotification,
    apiCall: apiCall
};