// Global variables and toggle function
let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// Global sidebar toggle function
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const mainContent = document.querySelector('.chat-main');
    if (sidebar && mainContent) {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    }
}

// Initialize message input and related functionality
let messageInput;
let sendButton;
let chatMessages;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) {
        console.error('Required UI elements not found');
        return;
    }

    // Initialize functionality
    initializePersonas();
    initializeScrolling();
    initializeMessageHandling();
    loadTopics();
});

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
        
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            container.scrollLeft += e.deltaY;
        });
    });
}

function initializeMessageHandling() {
    if (!messageInput || !sendButton) return;

    sendButton.addEventListener('click', handleMessageSend);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleMessageSend();
        }
    });
}

async function handleMessageSend() {
    if (!messageInput || !sendButton || !chatMessages) return;
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    messageInput.disabled = true;
    sendButton.disabled = true;
    sendButton.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        <span class="visually-hidden">Sending...</span>
    `;
    
    try {
        appendMessage('User', message);
        messageInput.value = '';
        
        const activeRole = getNextPersona();
        
        if (!currentThread) {
            const response = await fetch('/api/start_dialogue', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    role: activeRole,
                    context: message,
                    topic_id: selectedTopic
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.status === "success") {
                currentThread = data.thread_id;
                appendMessage(activeRole, data.response);
                await suggestTopics(message);
            } else {
                throw new Error(data.message || "Failed to start dialogue");
            }
        } else {
            const response = await fetch('/api/continue_dialogue', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    thread_id: currentThread,
                    role: activeRole,
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.status === "success") {
                appendMessage(activeRole, data.response);
            } else {
                throw new Error(data.message || "Failed to continue dialogue");
            }
        }
    } catch (error) {
        console.error('Error:', error);
        appendSystemMessage(`An error occurred: ${error.message}. Please try again.`);
        
        if (!currentThread) {
            currentThread = null;
        }
    } finally {
        if (messageInput && sendButton) {
            messageInput.disabled = false;
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="bi bi-send"></i>';
        }
    }
}

// Rest of the functions remain the same...
[Previous implementation of loadTopics, showLoading, showError, updateTopicsList, selectTopic, togglePersona, getNextPersona, suggestTopics, appendMessage, and appendSystemMessage functions]
