// Global variables with proper initialization
let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;
let conversationDirection = 'balanced';
let conversationFocus = 2;

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
    loadTopics();
});

function initializeUI() {
    // Initialize UI elements with error handling
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) {
        console.error('Required UI elements not found');
        showError('Failed to initialize chat interface');
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

async function sendMessage() {
    if (!messageInput.value.trim()) return;

    const message = messageInput.value;
    messageInput.value = '';

    // Add user message to chat
    addMessage('user', message);

    // Get next available persona
    const availableRoles = availablePersonas.filter(p => !excludedPersonas.has(p));
    if (availableRoles.length === 0) {
        showError('Please include at least one AI guide in the conversation');
        return;
    }

    currentPersonaIndex = (currentPersonaIndex + 1) % availableRoles.length;
    const respondingRole = availableRoles[currentPersonaIndex];

    try {
        const response = await fetch('/api/chat/continue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                thread_id: currentThread,
                role: respondingRole,
                input: message,
                style: {
                    direction: conversationDirection,
                    focus: conversationFocus
                }
            })
        });

        const data = await response.json();
        if (data.error) {
            showError(data.error);
            return;
        }

        addMessage(respondingRole, data.response);
        
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message');
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

async function loadTopics() {
    try {
        const response = await fetch('/api/topics');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading topics:', data.error);
            return;
        }
        
        updateTopicsList(data.topics);
        
    } catch (error) {
        console.error('Error loading topics:', error);
    }
}

function updateTopicsList(topics) {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) return;
    
    topicsList.innerHTML = '';
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
    const activeTopics = document.getElementById('active-topics');
    if (activeTopics) {
        const topicChip = document.createElement('div');
        topicChip.className = 'topic-chip';
        topicChip.textContent = topic.title;
        activeTopics.appendChild(topicChip);
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message message-system';
    errorDiv.innerHTML = `
        <strong>Error</strong>
        <p>${message}</p>
    `;
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const chatMain = document.querySelector('.chat-main');
    if (sidebar && chatMain) {
        sidebar.classList.toggle('open');
        chatMain.classList.toggle('sidebar-open');
    }
}
