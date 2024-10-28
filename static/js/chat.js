let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;
let touchStartX = 0;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    const topicsList = document.getElementById('topics-list');
    const activeTopics = document.getElementById('active-topics');
    const chatSidebar = document.getElementById('chatSidebar');
    
    initializePersonas();
    initializeScrolling();
    loadTopics();
    
    function initializePersonas() {
        document.querySelectorAll('.persona-card').forEach(card => {
            card.addEventListener('click', function() {
                const role = this.dataset.role;
                togglePersona(role, this);
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
    
    function initializeScrolling() {
        const scrollContainers = document.querySelectorAll('.personas-scroll, .topics-scroll');
        
        scrollContainers.forEach(container => {
            let isScrolling = false;
            let startX;
            let scrollLeft;
            
            container.addEventListener('touchstart', (e) => {
                isScrolling = true;
                startX = e.touches[0].pageX - container.offsetLeft;
                scrollLeft = container.scrollLeft;
                container.style.scrollBehavior = 'auto';
            });
            
            container.addEventListener('touchmove', (e) => {
                if (!isScrolling) return;
                e.preventDefault();
                const x = e.touches[0].pageX - container.offsetLeft;
                const walk = (x - startX) * 2;
                container.scrollLeft = scrollLeft - walk;
            });
            
            container.addEventListener('touchend', () => {
                isScrolling = false;
                container.style.scrollBehavior = 'smooth';
            });
            
            // Smooth mouse wheel scrolling
            container.addEventListener('wheel', (e) => {
                e.preventDefault();
                container.scrollLeft += e.deltaY;
            });
        });
    }
    
    function toggleSidebar() {
        chatSidebar.classList.toggle('open');
    }
    
    function togglePersona(role, element) {
        const allElements = document.querySelectorAll(`[data-role="${role}"]`);
        
        if (excludedPersonas.has(role)) {
            excludedPersonas.delete(role);
            allElements.forEach(el => {
                el.classList.remove('excluded');
                el.classList.add('active');
            });
        } else {
            excludedPersonas.add(role);
            allElements.forEach(el => {
                el.classList.add('excluded');
                el.classList.remove('active');
            });
        }
        
        // Visual feedback
        element.style.transform = 'scale(0.95)';
        setTimeout(() => {
            element.style.transform = '';
        }, 200);
    }
    
    function getNextPersona() {
        const activePersonas = availablePersonas.filter(p => !excludedPersonas.has(p));
        if (activePersonas.length === 0) return availablePersonas[0];
        currentPersonaIndex = (currentPersonaIndex + 1) % activePersonas.length;
        
        // Highlight active persona
        document.querySelectorAll('.persona-card').forEach(card => {
            card.classList.remove('active');
            if (card.dataset.role === activePersonas[currentPersonaIndex]) {
                card.classList.add('active');
                // Scroll into view if needed
                card.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            }
        });
        
        return activePersonas[currentPersonaIndex];
    }

    // Rest of the existing chat.js code...
    // [Previous message handling, topic suggestion, and other functionality remains unchanged]
});
