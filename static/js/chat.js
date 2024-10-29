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

// [Rest of the file remains unchanged...]
