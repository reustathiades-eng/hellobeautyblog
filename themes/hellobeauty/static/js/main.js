// =============================================================================
// HELLO BEAUTY BLOG - Main JavaScript
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // -------------------------------------------------------------------------
    // Mobile Menu Toggle
    // -------------------------------------------------------------------------
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            
            // Update aria-expanded
            const isExpanded = !mobileMenu.classList.contains('hidden');
            mobileMenuToggle.setAttribute('aria-expanded', isExpanded);
        });
    }
    
    // -------------------------------------------------------------------------
    // Search Overlay
    // -------------------------------------------------------------------------
    const searchToggle = document.getElementById('search-toggle');
    const searchOverlay = document.getElementById('search-overlay');
    const searchClose = document.getElementById('search-close');
    const searchContainer = document.getElementById('search-container');
    
    if (searchToggle && searchOverlay) {
        // Open search
        searchToggle.addEventListener('click', function() {
            searchOverlay.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
            // Initialize Pagefind if available
            if (window.PagefindUI && searchContainer) {
                if (!searchContainer.hasChildNodes()) {
                    new PagefindUI({
                        element: "#search-container",
                        showSubResults: true,
                        showImages: true
                    });
                }
                // Focus search input
                setTimeout(() => {
                    const input = searchContainer.querySelector('input');
                    if (input) input.focus();
                }, 100);
            }
        });
        
        // Close search
        if (searchClose) {
            searchClose.addEventListener('click', function() {
                searchOverlay.classList.add('hidden');
                document.body.style.overflow = '';
            });
        }
        
        // Close on overlay click
        searchOverlay.addEventListener('click', function(e) {
            if (e.target === searchOverlay) {
                searchOverlay.classList.add('hidden');
                document.body.style.overflow = '';
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !searchOverlay.classList.contains('hidden')) {
                searchOverlay.classList.add('hidden');
                document.body.style.overflow = '';
            }
        });
    }
    
    // -------------------------------------------------------------------------
    // Lazy Loading Images
    // -------------------------------------------------------------------------
    if ('loading' in HTMLImageElement.prototype) {
        // Native lazy loading supported
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src || img.src;
        });
    } else {
        // Fallback for older browsers
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }
    
    // -------------------------------------------------------------------------
    // Smooth Scroll for Anchor Links
    // -------------------------------------------------------------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // -------------------------------------------------------------------------
    // Sticky Header Shadow on Scroll
    // -------------------------------------------------------------------------
    const header = document.querySelector('header');
    if (header) {
        let lastScroll = 0;
        
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 10) {
                header.classList.add('shadow-md');
            } else {
                header.classList.remove('shadow-md');
            }
            
            lastScroll = currentScroll;
        }, { passive: true });
    }
    
    // -------------------------------------------------------------------------
    // Newsletter Form Submission
    // -------------------------------------------------------------------------
    const newsletterForms = document.querySelectorAll('form[action*="formspree"]');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: { 'Accept': 'application/json' }
                });
                
                if (response.ok) {
                    form.innerHTML = '<p class="text-green-600 font-medium">✓ Thank you for subscribing!</p>';
                } else {
                    throw new Error('Submission failed');
                }
            } catch (error) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                alert('Sorry, there was an error. Please try again.');
            }
        });
    });
    
    // -------------------------------------------------------------------------
    // Product Image Zoom (for product pages)
    // -------------------------------------------------------------------------
    const productGallery = document.querySelector('.product-single__gallery img');
    if (productGallery) {
        productGallery.style.cursor = 'zoom-in';
        productGallery.addEventListener('click', function() {
            if (this.style.transform === 'scale(1.5)') {
                this.style.transform = 'scale(1)';
                this.style.cursor = 'zoom-in';
            } else {
                this.style.transform = 'scale(1.5)';
                this.style.cursor = 'zoom-out';
            }
        });
    }
    
    // -------------------------------------------------------------------------
    // Affiliate Link Tracking (basic)
    // -------------------------------------------------------------------------
    document.querySelectorAll('a[rel*="sponsored"]').forEach(link => {
        link.addEventListener('click', function() {
            // Track with Plausible if available
            if (window.plausible) {
                plausible('Affiliate Click', {
                    props: {
                        url: this.href,
                        product: document.title
                    }
                });
            }
        });
    });
    
});

// =============================================================================
// Utility Functions
// =============================================================================

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
