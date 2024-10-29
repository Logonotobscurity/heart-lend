// Global variables with proper initialization
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

function initializeScrolling() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
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
    
    // Check if any personas are selected
    if (selectedPersonas.size === 0) {
        showError('Please select at least one AI guide to join the conversation');
        return;
    }

    // Get array of selected personas
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

// ... [rest of the file remains unchanged] ...
