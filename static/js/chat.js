// Global variables
let currentThread = null;
let selectedTopic = null;
let selectedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;
let conversationDirection = 'balanced';
let conversationFocus = 2;
let isLoading = false;

// Constants
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// DOM Elements
let messageInput;
let sendButton;
let chatMessages;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    initializePersonas();
    initializeMessageHandling();
    initializeDirectionControls();
    loadTopicsWithRetry();
});

// Add global error handling for unhandled rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showError('An unexpected error occurred. Please try again.');
});

function initializeUI() {
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) {
        console.error('Required UI elements not found');
        return;
    }
}

function initializePersonas() {
    const personaCards = document.querySelectorAll('.persona-card');
    personaCards.forEach(card => {
        card.addEventListener('click', () => {
            const role = card.dataset.role;
            if (card.classList.contains('active')) {
                selectedPersonas.delete(role);
                card.classList.remove('active');
            } else {
                selectedPersonas.add(role);
                card.classList.add('active');
            }
        });
    });
}

function initializeDirectionControls() {
    const directionButtons = document.querySelectorAll('.direction-buttons .btn');
    const focusSlider = document.getElementById('focusSlider');
    const focusValue = document.querySelector('.focus-value');

    if (directionButtons) {
        directionButtons.forEach(button => {
            button.addEventListener('click', () => {
                directionButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                conversationDirection = button.dataset.direction;
            });
        });
    }

    if (focusSlider && focusValue) {
        focusSlider.addEventListener('input', () => {
            conversationFocus = parseFloat(focusSlider.value);
            updateFocusLabel(focusValue, conversationFocus);
        });
    }
}

function initializeMessageHandling() {
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
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

async function loadTopicsWithRetry(retries = MAX_RETRIES) {
    try {
        const response = await fetch('/api/topics');
        if (!response.ok) {
            throw new Error(`Failed to load topics: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateTopicsList(data.topics || []);
        
    } catch (error) {
        console.error('Error loading topics:', error);
        
        if (retries > 0) {
            setTimeout(() => loadTopicsWithRetry(retries - 1), RETRY_DELAY);
        } else {
            showError('Unable to load topics. Please refresh the page.');
        }
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

        if (!response.ok) {
            throw new Error(`Failed to send message: ${response.statusText}`);
        }
        
        const result = await response.json();
        if (result.error) {
            throw new Error(result.error);
        }
        
        return result.data;
        
    } catch (error) {
        console.error('Error sending message:', error);
        
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
    
    if (selectedPersonas.size === 0) {
        showError('Please select at least one AI guide');
        return;
    }

    const activePersonas = Array.from(selectedPersonas);
    currentPersonaIndex = (currentPersonaIndex + 1) % activePersonas.length;
    const respondingRole = activePersonas[currentPersonaIndex];

    messageInput.value = '';
    isLoading = true;
    addLoadingIndicator();

    try {
        const requestData = currentThread ? {
            thread_id: currentThread,
            role: respondingRole,
            input: message,
            selected_personas: Array.from(selectedPersonas),
            style: {
                direction: conversationDirection,
                focus: conversationFocus
            }
        } : {
            role: respondingRole,
            selected_personas: Array.from(selectedPersonas),
            context: message
        };

        addMessage('user', message);
        const response = await sendMessageWithRetry(requestData);
        
        if (!currentThread && response.thread_id) {
            currentThread = response.thread_id;
        }

        addMessage(respondingRole, response.response);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to send message');
    } finally {
        isLoading = false;
        removeLoadingIndicator();
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
