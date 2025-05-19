document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Flash messages auto-close
    const alertMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    alertMessages.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Seat selection logic for trip detail page
    const seatRadios = document.querySelectorAll('.seat-radio');
    if (seatRadios.length > 0) {
        seatRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                // Remove selected class from all seats
                document.querySelectorAll('.seat label').forEach(seat => {
                    seat.classList.remove('selected');
                });
                
                // Add selected class to the chosen seat
                if (this.checked) {
                    this.nextElementSibling.classList.add('selected');
                }
            });
        });
    }

    // Date picker default to today
    const departureDateInputs = document.querySelectorAll('input[type="date"]');
    departureDateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date();
            let dd = today.getDate();
            let mm = today.getMonth() + 1;
            const yyyy = today.getFullYear();
            
            if (dd < 10) {
                dd = '0' + dd;
            }
            
            if (mm < 10) {
                mm = '0' + mm;
            }
            
            input.value = yyyy + '-' + mm + '-' + dd;
            input.min = yyyy + '-' + mm + '-' + dd;
        }
    });

    // Custom form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // Toggle password visibility
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('data-toggle'));
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });

    // Search form enhancements
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        // Swap origin and destination
        const swapButton = document.querySelector('.swap-locations');
        if (swapButton) {
            swapButton.addEventListener('click', function() {
                const departureCity = document.getElementById('id_departure_city');
                const arrivalCity = document.getElementById('id_arrival_city');
                
                const tempValue = departureCity.value;
                departureCity.value = arrivalCity.value;
                arrivalCity.value = tempValue;
            });
        }
    }

    // Countdown timer for booking process
    const countdownElement = document.querySelector('.countdown-timer');
    if (countdownElement) {
        let timeLeft = 10 * 60; // 10 minutes in seconds
        
        const countdownInterval = setInterval(function() {
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                countdownElement.innerHTML = "Hết thời gian";
                
                // Redirect to home page after 3 seconds
                setTimeout(function() {
                    window.location.href = '/';
                }, 3000);
                
                return;
            }
            
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            countdownElement.innerHTML = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            timeLeft--;
        }, 1000);
    }

    // Image lazy loading
    const lazyImages = document.querySelectorAll('img.lazy');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const image = entry.target;
                    image.src = image.dataset.src;
                    image.classList.remove('lazy');
                    imageObserver.unobserve(image);
                }
            });
        });
        
        lazyImages.forEach(function(image) {
            imageObserver.observe(image);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        let lazyLoadThrottleTimeout;
        
        function lazyLoad() {
            if (lazyLoadThrottleTimeout) {
                clearTimeout(lazyLoadThrottleTimeout);
            }
            
            lazyLoadThrottleTimeout = setTimeout(function() {
                const scrollTop = window.pageYOffset;
                
                lazyImages.forEach(function(img) {
                    if (img.offsetTop < (window.innerHeight + scrollTop)) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                    }
                });
                
                if (lazyImages.length === 0) {
                    document.removeEventListener('scroll', lazyLoad);
                    window.removeEventListener('resize', lazyLoad);
                    window.removeEventListener('orientationChange', lazyLoad);
                }
            }, 20);
        }
        
        document.addEventListener('scroll', lazyLoad);
        window.addEventListener('resize', lazyLoad);
        window.addEventListener('orientationChange', lazyLoad);
    }

    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
