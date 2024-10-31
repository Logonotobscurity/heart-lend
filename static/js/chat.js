// Global variables with proper initialization
let currentThread = null;
let selectedTopic = null;
let activePersonas = new Set();
let conversationDirection = 'balanced';
let conversationFocus = 2;
let isLoading = false;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;
const MAX_DELAY = 8000;

// Initialize logger
const logger = {
    info: (msg) => console.log(msg),
    error: (msg, err) => console.error(msg, err)
};

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
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) {
        showError('Required UI elements not found. Please refresh the page.');
        logger.error('Required UI elements not found');
        return;
    }
}

async function loadTopicsWithRetry(retries = MAX_RETRIES) {
    let currentDelay = RETRY_DELAY;
    let lastError = null;
    
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            // Add loading indicator
            if (attempt === 0) {
                showLoading('Loading topics...');
            }

            const response = await fetch('/api/topics');
            const result = await response.json();

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            if (result.status === 'error') {
                throw new Error(result.message || 'Unknown error occurred');
            }
            
            if (!result.data || !result.data.topics) {
                throw new Error('Invalid response format');
            }
            
            // Remove loading indicator
            hideLoading();
            
            logger.info(`Successfully loaded ${result.data.topics.length} topics`);
            updateTopicsList(result.data.topics);
            return;
            
        } catch (error) {
            lastError = error;
            logger.error('Error loading topics:', error);
            
            if (attempt < retries - 1) {
                const delay = Math.min(currentDelay * (2 ** attempt), MAX_DELAY);
                logger.info(`Retrying in ${delay}ms... (Attempt ${attempt + 1}/${retries})`);
                await new Promise(resolve => setTimeout(resolve, delay));
                continue;
            }
            
            // Remove loading indicator and show error
            hideLoading();
            showError('Unable to load topics. Please refresh the page to try again.');
            updateTopicsList([]); // Show empty state
        }
    }

    return null;
}

function showLoading(message) {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-indicator';
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">${message}</p>
    `;
    
    const topicsList = document.getElementById('topics-list');
    if (topicsList) {
        topicsList.innerHTML = '';
        topicsList.appendChild(loadingDiv);
    }
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function updateTopicsList(topics) {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) {
        logger.error('Topics list container not found');
        return;
    }
    
    topicsList.innerHTML = '';
    
    if (!topics || topics.length === 0) {
        topicsList.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                <span>No topics available at the moment.</span>
                <button class="btn btn-link btn-sm ms-2" onclick="loadTopicsWithRetry()">
                    <i class="bi bi-arrow-clockwise"></i> Refresh
                </button>
            </div>`;
        return;
    }
    
    // Group topics by category
    const groupedTopics = topics.reduce((acc, topic) => {
        if (!acc[topic.category]) {
            acc[topic.category] = [];
        }
        acc[topic.category].push(topic);
        return acc;
    }, {});
    
    // Create category sections
    Object.entries(groupedTopics).forEach(([category, categoryTopics]) => {
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section mb-4';
        
        categorySection.innerHTML = `
            <h4 class="category-title h6 mb-3">${category}</h4>
            <div class="category-topics"></div>
        `;
        
        const topicsContainer = categorySection.querySelector('.category-topics');
        
        categoryTopics.forEach(topic => {
            const topicButton = document.createElement('button');
            topicButton.className = 'topic-button';
            topicButton.innerHTML = `
                <h3 class="topic-title">${topic.title}</h3>
                <p class="topic-description">${topic.description}</p>
            `;
            
            topicButton.addEventListener('click', () => selectTopic(topic));
            topicsContainer.appendChild(topicButton);
        });
        
        topicsList.appendChild(categorySection);
    });
}

function showError(message, duration = 5000) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        <i class="bi bi-exclamation-triangle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    if (duration > 0) {
        setTimeout(() => {
            errorDiv.classList.add('fade');
            setTimeout(() => errorDiv.remove(), 300);
        }, duration);
    }
}

// Initialize persona selection
function initializePersonas() {
    const personaCards = document.querySelectorAll('.persona-card');
    personaCards.forEach(card => {
        card.addEventListener('click', () => togglePersona(card));
    });
}

// Initialize smooth scrolling
function initializeScrolling() {
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize message handling
function initializeMessageHandling() {
    if (messageInput && sendButton) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        sendButton.addEventListener('click', sendMessage);
    }
}

// Initialize direction controls
function initializeDirectionControls() {
    const directionButtons = document.querySelectorAll('.direction-buttons .btn');
    const focusSlider = document.getElementById('focusSlider');
    
    directionButtons.forEach(button => {
        button.addEventListener('click', () => {
            directionButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            conversationDirection = button.dataset.direction;
        });
    });
    
    if (focusSlider) {
        focusSlider.addEventListener('input', (e) => {
            conversationFocus = parseFloat(e.target.value);
            updateFocusLabel(conversationFocus);
        });
    }
}

function updateFocusLabel(value) {
    const focusLabel = document.querySelector('.focus-value');
    if (focusLabel) {
        if (value < 1.5) focusLabel.textContent = 'Practical';
        else if (value < 2.5) focusLabel.textContent = 'Balanced';
        else focusLabel.textContent = 'Philosophical';
    }
}

// Export functions for testing
window.loadTopicsWithRetry = loadTopicsWithRetry;
window.updateTopicsList = updateTopicsList;
window.showError = showError;
