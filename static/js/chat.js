// Conversation Direction State
let conversationState = {
    style: 'balanced',
    depth: 1.5
};

// Function declarations
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const mainContent = document.querySelector('.chat-main');
    if (sidebar && mainContent) {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    }
}

// Initialize all components
document.addEventListener('DOMContentLoaded', function() {
    initializeDirectionControls();
    initializePersonas();
    initializeScrolling();
    initializeMessageHandling();
    initializeVisualization();
    loadTopics();
});

// Direction Control Functions
function initializeDirectionControls() {
    // Style buttons
    document.querySelectorAll('.style-buttons .btn').forEach(button => {
        button.addEventListener('click', function() {
            const style = this.dataset.style;
            setConversationStyle(style);
        });
    });

    // Depth slider
    const depthSlider = document.getElementById('depthSlider');
    if (depthSlider) {
        depthSlider.addEventListener('input', function() {
            setConversationDepth(parseFloat(this.value));
        });
    }
}

function setConversationStyle(style) {
    conversationState.style = style;
    
    // Update UI
    document.querySelectorAll('.style-buttons .btn').forEach(button => {
        button.classList.remove('active');
        if (button.dataset.style === style) {
            button.classList.add('active');
        }
    });
}

function setConversationDepth(depth) {
    conversationState.depth = depth;
    document.getElementById('dialogue-depth').textContent = depth.toFixed(1);
}

// Global variables for visualization
let interactionGraph = null;
let conversationData = {
    activePersonas: new Set(),
    interactions: [],
    messageCount: 0,
    dialogueDepth: 0
};

// Global variables for chat
let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;

// Initialize message input and related functionality
let messageInput;
let sendButton;
let chatMessages;

// Visualization Functions
function initializeVisualization() {
    const ctx = document.getElementById('interaction-graph');
    if (!ctx) return;

    interactionGraph = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [],
            datasets: [{
                label: 'Interaction Patterns',
                data: [],
                fill: true,
                backgroundColor: 'rgba(var(--bs-primary-rgb), 0.2)',
                borderColor: 'rgb(var(--bs-primary-rgb))',
                pointBackgroundColor: 'rgb(var(--bs-primary-rgb))',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(var(--bs-primary-rgb))'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: 'rgba(var(--bs-secondary-rgb), 0.1)'
                    },
                    grid: {
                        color: 'rgba(var(--bs-secondary-rgb), 0.1)'
                    },
                    ticks: {
                        display: false
                    }
                }
            }
        }
    });

    updateVisualization();
}

function updateVisualization() {
    if (!interactionGraph) return;

    document.getElementById('active-personas-count').textContent = conversationData.activePersonas.size;
    document.getElementById('total-interactions').textContent = conversationData.messageCount;
    document.getElementById('dialogue-depth').textContent = conversationData.dialogueDepth.toFixed(1);

    const labels = Array.from(conversationData.activePersonas);
    const data = labels.map(persona => {
        return conversationData.interactions.filter(i => i.persona === persona).length;
    });

    interactionGraph.data.labels = labels;
    interactionGraph.data.datasets[0].data = data;
    interactionGraph.update();
}

function recordInteraction(persona, message) {
    conversationData.activePersonas.add(persona);
    conversationData.interactions.push({
        persona,
        message,
        timestamp: new Date(),
        style: conversationState.style,
        depth: conversationState.depth
    });
    conversationData.messageCount++;
    conversationData.dialogueDepth = Math.min(
        (conversationData.messageCount / 2) * 0.5,
        3
    );
    
    updateVisualization();
}

// Chat Functions
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
                recordInteraction(activeRole, data.response);
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
                recordInteraction(activeRole, data.response);
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

// Helper Functions
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

// The rest of the code (persona management, topic management, etc.) remains unchanged
