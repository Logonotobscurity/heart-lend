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
function handleMessageSend() {
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
    
    (async () => {
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
    })();
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
        appendSystemMessage('Failed to initialize chat interface. Please refresh the page.');
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

[Rest of the file remains unchanged...]
