// Global variables
let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;

// Utility functions
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
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
            card.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
    });
    
    return activePersonas[currentPersonaIndex];
}

async function loadTopics() {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) return;
    
    // Show loading state
    topicsList.innerHTML = `
        <div class="loading-indicator text-center py-4">
            <div class="spinner-border text-primary mb-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading topics...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/topics', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const topics = await response.json();
        updateTopicsList(topics);
    } catch (error) {
        console.error('Error loading topics:', error);
        topicsList.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Failed to load topics. Please refresh the page to try again.
            </div>
        `;
    }
}

function updateTopicsList(topics) {
    const topicsList = document.getElementById('topics-list');
    const activeTopics = document.getElementById('active-topics');
    
    if (!topicsList) return;
    
    if (topics.length === 0) {
        topicsList.innerHTML = `
            <div class="placeholder-text text-center py-4">
                <i class="bi bi-lightbulb fs-2 mb-3"></i>
                <p>Start a conversation to receive personalized topic suggestions</p>
            </div>
        `;
        return;
    }
    
    topicsList.innerHTML = topics.map(topic => `
        <button class="topic-button" data-topic-id="${topic.id}">
            <h6 class="topic-title mb-1">${topic.title}</h6>
            <span class="topic-category">${topic.category}</span>
            <p class="topic-description mb-0">${topic.description}</p>
        </button>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('[data-topic-id]').forEach(button => {
        button.addEventListener('click', function() {
            selectTopic(this.dataset.topicId, this);
        });
    });
}

function selectTopic(topicId, element) {
    selectedTopic = topicId;
    
    // Update visual state
    document.querySelectorAll('[data-topic-id]').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.topicId === topicId) {
            el.classList.add('active');
        }
    });
    
    if (!currentThread) {
        const title = element.querySelector('.topic-title')?.textContent || 
                     element.textContent;
        messageInput.placeholder = `Start a conversation about: ${title}`;
    }
}

async function suggestTopics(context) {
    try {
        const response = await fetch('/api/topics/suggest', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ context })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === "success") {
            updateTopicsList(data.topics);
        } else {
            throw new Error(data.message || "Failed to suggest topics");
        }
    } catch (error) {
        console.error('Error suggesting topics:', error);
        appendSystemMessage('Unable to generate topic suggestions. The conversation will continue.');
    }
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    
    // Initialize components
    initializePersonas();
    initializeScrolling();
    loadTopics();
    
    function initializePersonas() {
        document.querySelectorAll('.persona-card').forEach(card => {
            card.addEventListener('click', function() {
                togglePersona(this.dataset.role, this);
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

    // Message handling
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    sendButton.addEventListener('click', async function() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        try {
            appendMessage('User', message);
            messageInput.value = '';
            
            const activeRole = getNextPersona();
            const response = await fetch('/api/topics/suggest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ context: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.status === "success") {
                updateTopicsList(data.topics);
            }
            
            appendMessage(activeRole, "Based on your message, I've suggested some related topics for our discussion. Feel free to explore them or continue our conversation.");
            
        } catch (error) {
            console.error('Error:', error);
            appendSystemMessage(`An error occurred: ${error.message}. Please try again.`);
        } finally {
            messageInput.disabled = false;
            sendButton.disabled = false;
        }
    });
    
    function appendMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role.toLowerCase().split(' ')[0]}`;
        messageDiv.innerHTML = `
            <strong>${role}:</strong>
            <p>${content}</p>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function appendSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-system';
        messageDiv.innerHTML = `
            <strong>System:</strong>
            <p class="text-danger">${content}</p>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
