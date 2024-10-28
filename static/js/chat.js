// Function declarations
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const mainContent = document.querySelector('.chat-main');
    if (sidebar && mainContent) {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    }
}

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
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

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

async function loadTopics() {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) return;
    
    try {
        showLoading(topicsList);
        const response = await fetch('/api/topics');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const topics = await response.json();
        updateTopicsList(topics);
    } catch (error) {
        console.error('Error loading topics:', error);
        showError(topicsList, 'Failed to load topics. Please refresh the page to try again.');
    }
}

function showLoading(element) {
    element.innerHTML = `
        <div class="loading-indicator text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading topics...</p>
        </div>
    `;
}

function showError(element, message) {
    element.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
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
    
    if (activeTopics) {
        activeTopics.innerHTML = topics.map(topic => `
            <div class="topic-chip" data-topic-id="${topic.id}">
                ${topic.title}
            </div>
        `).join('');
    }
    
    // Add click handlers
    document.querySelectorAll('[data-topic-id]').forEach(button => {
        button.addEventListener('click', function() {
            selectTopic(this.dataset.topicId, this);
        });
    });
}

function selectTopic(topicId, element) {
    selectedTopic = topicId;
    
    document.querySelectorAll('[data-topic-id]').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.topicId === topicId) {
            el.classList.add('active');
        }
    });
    
    if (!currentThread && messageInput) {
        const title = element.querySelector('.topic-title')?.textContent || 
                     element.textContent;
        messageInput.placeholder = `Start a conversation about: ${title}`;
    }
}

function togglePersona(role, element) {
    if (!element) return;
    
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

async function suggestTopics(context) {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) return;
    
    try {
        showLoading(topicsList);
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
        showError(topicsList, 'Unable to generate topic suggestions. The conversation will continue.');
    }
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

function appendMessage(role, content) {
    if (!chatMessages) return;
    
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
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-system';
    messageDiv.innerHTML = `
        <strong>System:</strong>
        <p class="text-danger">${content}</p>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
