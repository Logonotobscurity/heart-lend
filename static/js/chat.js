// Existing code remains the same until initializePersonas()

function initializePersonas() {
    document.querySelectorAll('.persona-card').forEach(card => {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        
        // Handle click/tap for selection
        card.addEventListener('click', function(e) {
            const role = this.dataset.role;
            
            // Check if the click was part of a swipe
            if (Math.abs(touchEndX - touchStartX) > 5 || Math.abs(touchEndY - touchStartY) > 5) {
                return;
            }
            
            // Toggle flip state
            this.classList.toggle('flipped');
            
            // After a delay, handle the selection
            setTimeout(() => {
                if (!this.classList.contains('flipped')) {
                    togglePersona(role, this);
                }
            }, 300);
        });
        
        // Touch events for better mobile handling
        card.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });
        
        card.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].clientX;
            touchEndY = e.changedTouches[0].clientY;
            
            // Calculate swipe distance
            const diffX = touchEndX - touchStartX;
            const diffY = touchEndY - touchStartY;
            
            // If it's a clear swipe, don't trigger flip
            if (Math.abs(diffX) > 50 || Math.abs(diffY) > 50) {
                return;
            }
        });
        
        // Add touch feedback
        card.addEventListener('touchstart', () => {
            card.style.transform = 'scale(0.95)';
        });
        
        card.addEventListener('touchend', () => {
            card.style.transform = '';
        });
    });
}

// Rest of the existing code remains unchanged
