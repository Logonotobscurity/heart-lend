// Global variables with proper initialization
let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Quantum Observer", 
    "Existential Explorer", "Kara the Visionary Dreamer"
];
let currentPersonaIndex = 0;
let conversationDirection = 'balanced';
let conversationFocus = 2;
let isLoading = false;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// DOM elements
let messageInput;
let sendButton;
let chatMessages;

// Initialize all functionality when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeUI();
    initializePersonas();
    initializeScrolling();
    initializeMessageHandling();
    initializeDirectionControls();
    loadTopicsWithRetry();
});

function initializeUI() {
    // Initialize UI elements with error handling
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) {
        showError('Required UI elements not found. Please refresh the page.');
        console.error('Required UI elements not found');
        return;
    }
}

function initializePersonas() {
    const personaCards = document.querySelectorAll('.persona-card');
    personaCards.forEach(card => {
        card.addEventListener('click', () => {
            const role = card.dataset.role;
            if (excludedPersonas.has(role)) {
                excludedPersonas.delete(role);
                card.classList.remove('excluded');
            } else {
                excludedPersonas.add(role);
                card.classList.add('excluded');
            }
        });
    });
}

function initializeScrolling() {
    // Enable smooth scrolling for chat messages
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function initializeMessageHandling() {
    // Handle message sending
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function initializeDirectionControls() {
    // Direction buttons
    const directionButtons = document.querySelectorAll('.direction-buttons .btn');
    directionButtons.forEach(button => {
        button.addEventListener('click', () => {
            directionButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            conversationDirection = button.dataset.direction;
        });
    });

    // Focus slider
    const focusSlider = document.getElementById('focusSlider');
    const focusValue = document.querySelector('.focus-value');
    if (focusSlider && focusValue) {
        focusSlider.addEventListener('input', () => {
            conversationFocus = parseFloat(focusSlider.value);
            updateFocusLabel(focusValue, conversationFocus);
        });
    }
}

function updateFocusLabel(element, value) {
    if (value < 1.5) {
        element.textContent = 'Practical';
    } else if (value < 2.5) {
        element.textContent = 'Balanced';
    } else {
        element.textContent = 'Philosophical';
    }
}

async function sendMessageWithRetry(data, retries = MAX_RETRIES) {
    const endpoint = currentThread ? '/api/chat/continue' : '/api/chat/start';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Failed to send message');
        }
        
        if (result.status === 'error') {
            throw new Error(result.message);
        }
        
        return result.data;
    } catch (error) {
        if (retries > 0 && !error.message.includes('thread not found')) {
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
            return sendMessageWithRetry(data, retries - 1);
        }
        throw error;
    }
}

async function sendMessage() {
    if (isLoading) return;
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Get next available persona
    const availableRoles = availablePersonas.filter(p => !excludedPersonas.has(p));
    if (availableRoles.length === 0) {
        showError('Please include at least one AI guide in the conversation');
        return;
    }

    currentPersonaIndex = (currentPersonaIndex + 1) % availableRoles.length;
    const respondingRole = availableRoles[currentPersonaIndex];

    messageInput.value = '';
    isLoading = true;
    addLoadingIndicator();

    try {
        const requestData = currentThread ? {
            thread_id: currentThread,
            role: respondingRole,
            input: message,
            style: {
                direction: conversationDirection,
                focus: conversationFocus
            }
        } : {
            role: respondingRole,
            context: message
        };

        // Add user message to chat
        addMessage('user', message);

        const response = await sendMessageWithRetry(requestData);
        
        if (!currentThread && response.thread_id) {
            currentThread = response.thread_id;
        }

        addMessage(respondingRole, response.response);

    } catch (error) {
        console.error('Error sending message:', error);
        showError(error.message || 'Failed to send message. Please try again.');
    } finally {
        isLoading = false;
        removeLoadingIndicator();
    }
}

async function loadTopicsWithRetry(retries = MAX_RETRIES) {
    try {
        const response = await fetch('/api/topics');
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Failed to load topics');
        }
        
        if (result.status === 'error') {
            throw new Error(result.message);
        }
        
        updateTopicsList(result.data.topics);
        
    } catch (error) {
        console.error('Error loading topics:', error);
        
        if (retries > 0) {
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
            return loadTopicsWithRetry(retries - 1);
        }
        
        showError('Unable to load topics. Please refresh the page.');
    }
}

function updateTopicsList(topics) {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) return;
    
    topicsList.innerHTML = '';
    
    if (!topics || topics.length === 0) {
        topicsList.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                No topics available at the moment.
            </div>`;
        return;
    }
    
    topics.forEach(topic => {
        const topicButton = document.createElement('button');
        topicButton.className = 'topic-button';
        topicButton.innerHTML = `
            <span class="topic-category">${topic.category}</span>
            <h3 class="topic-title">${topic.title}</h3>
            <p class="topic-description">${topic.description}</p>
        `;
        
        topicButton.addEventListener('click', () => selectTopic(topic));
        topicsList.appendChild(topicButton);
    });
}

function selectTopic(topic) {
    selectedTopic = topic;
    document.querySelectorAll('.topic-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
    
    // Update active topics display
    updateActiveTopics(topic);
}

function updateActiveTopics(topic) {
    const activeTopics = document.getElementById('active-topics');
    if (!activeTopics) return;
    
    const existingChip = Array.from(activeTopics.children)
        .find(chip => chip.textContent === topic.title);
        
    if (!existingChip) {
        const topicChip = document.createElement('div');
        topicChip.className = 'topic-chip';
        topicChip.textContent = topic.title;
        activeTopics.appendChild(topicChip);
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role === 'user' ? 'user' : 'ai'}`;
    
    if (role !== 'user') {
        const roleHeader = document.createElement('strong');
        roleHeader.textContent = role;
        messageDiv.appendChild(roleHeader);
    }
    
    const contentP = document.createElement('p');
    contentP.textContent = content;
    messageDiv.appendChild(contentP);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingIndicator() {
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message message-system';
    errorDiv.innerHTML = `
        <strong><i class="bi bi-exclamation-triangle me-2"></i>Error</strong>
        <p>${message}</p>
    `;
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.classList.add('fade-out');
        setTimeout(() => errorDiv.remove(), 500);
    }, 5000);
}

function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const chatMain = document.querySelector('.chat-main');
    if (sidebar && chatMain) {
        sidebar.classList.toggle('open');
        chatMain.classList.toggle('sidebar-open');
    }
}