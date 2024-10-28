// Global variables for chat
let messageInput = null;
let sendButton = null;
let chatMessages = null;
let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;

// Conversation Direction State
let conversationState = {
    style: 'balanced',
    depth: 1.5
};

// Message Handling Functions
async function handleMessageSend() {
    if (!messageInput || !sendButton || !chatMessages) {
        console.error('Required chat elements not found');
        return;
    }
    
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
                    topic_id: selectedTopic,
                    style: conversationState.style,
                    depth: conversationState.depth
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
                    message: message,
                    style: conversationState.style,
                    depth: conversationState.depth
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
    if (!chatMessages) {
        console.error('Chat messages container not found');
        return;
    }
    
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
    if (!chatMessages) {
        console.error('Chat messages container not found');
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-system';
    messageDiv.innerHTML = `
        <strong>System:</strong>
        <p class="text-danger">${content}</p>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initialize all components
document.addEventListener('DOMContentLoaded', function() {
    initializeMessageHandling();
    initializeDirectionControls();
    initializePersonas();
    initializeScrolling();
    loadTopics();
});

// Initialize Message Handling
function initializeMessageHandling() {
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) {
        console.error('Failed to initialize chat elements');
        return;
    }

    sendButton.addEventListener('click', handleMessageSend);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleMessageSend();
        }
    });
}

// Direction Control Functions
function initializeDirectionControls() {
    document.querySelectorAll('.style-buttons .btn').forEach(button => {
        button.addEventListener('click', function() {
            const style = this.dataset.style;
            setConversationStyle(style);
        });
    });

    const depthSlider = document.getElementById('depthSlider');
    if (depthSlider) {
        depthSlider.addEventListener('input', function() {
            setConversationDepth(parseFloat(this.value));
        });
    }
}

function setConversationStyle(style) {
    conversationState.style = style;
    
    document.querySelectorAll('.style-buttons .btn').forEach(button => {
        button.classList.remove('active');
        if (button.dataset.style === style) {
            button.classList.add('active');
        }
    });
}

function setConversationDepth(depth) {
    conversationState.depth = depth;
}

// Persona Management
function initializePersonas() {
    document.querySelectorAll('.persona-card').forEach(card => {
        card.addEventListener('click', function() {
            const role = this.dataset.role;
            togglePersona(role, this);
        });
    });
}

function togglePersona(role, element) {
    if (!element) return;
    
    if (excludedPersonas.has(role)) {
        excludedPersonas.delete(role);
        element.classList.remove('excluded');
        element.classList.add('active');
    } else {
        excludedPersonas.add(role);
        element.classList.add('excluded');
        element.classList.remove('active');
    }
}

function getNextPersona() {
    const activePersonas = availablePersonas.filter(p => !excludedPersonas.has(p));
    if (activePersonas.length === 0) return availablePersonas[0];
    
    currentPersonaIndex = (currentPersonaIndex + 1) % activePersonas.length;
    
    document.querySelectorAll('.persona-card').forEach(card => {
        card.classList.remove('active');
        if (card.dataset.role === activePersonas[currentPersonaIndex]) {
            card.classList.add('active');
        }
    });
    
    return activePersonas[currentPersonaIndex];
}

// Initialize Scrolling
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
        });
    });
}

// Topic Management
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
        }
    } catch (error) {
        console.error('Error suggesting topics:', error);
    }
}

function updateTopicsList(topics) {
    const topicsList = document.getElementById('topics-list');
    if (!topicsList) return;
    
    topicsList.innerHTML = topics.map(topic => `
        <div class="topic-card" data-topic-id="${topic.id}">
            <h3 class="topic-title h6">${topic.title}</h3>
            <p class="topic-description small">${topic.description}</p>
            <span class="badge bg-secondary">${topic.category}</span>
        </div>
    `).join('');
    
    // Add click handlers to new topic cards
    topicsList.querySelectorAll('.topic-card').forEach(card => {
        card.addEventListener('click', () => {
            selectedTopic = card.dataset.topicId;
            document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
        });
    });
}

// Load initial topics
async function loadTopics() {
    try {
        const response = await fetch('/api/topics');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const topics = await response.json();
        updateTopicsList(topics);
    } catch (error) {
        console.error('Error loading topics:', error);
        const topicsList = document.getElementById('topics-list');
        if (topicsList) {
            topicsList.innerHTML = '<p class="text-danger">Failed to load topics. Please try again later.</p>';
        }
    }
}

// Sidebar Toggle
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const mainContent = document.querySelector('.chat-main');
    if (sidebar && mainContent) {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    }
}
