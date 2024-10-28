// Conversation Direction State
let conversationState = {
    style: 'balanced',
    depth: 1.5
};

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
let messageInput;
let sendButton;
let chatMessages;

// Initialize all components
document.addEventListener('DOMContentLoaded', function() {
    initializeDirectionControls();
    initializePersonas();
    initializeScrolling();
    initializeMessageHandling();
    initializeVisualization();
    loadTopics();
});

// Persona Management Functions
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
}

function getNextPersona() {
    const activePersonas = availablePersonas.filter(p => !excludedPersonas.has(p));
    if (activePersonas.length === 0) return availablePersonas[0];
    
    currentPersonaIndex = (currentPersonaIndex + 1) % activePersonas.length;
    
    document.querySelectorAll('.persona-card').forEach(card => {
        card.classList.remove('active');
        if (card.dataset.role === activePersonas[currentPersonaIndex]) {
            card.classList.add('active');
            card.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
    });
    
    return activePersonas[currentPersonaIndex];
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
    document.getElementById('dialogue-depth').textContent = depth.toFixed(1);
}

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

// Initialize Message Handling
function initializeMessageHandling() {
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-message');
    chatMessages = document.getElementById('chat-messages');
    
    if (!messageInput || !sendButton || !chatMessages) return;

    sendButton.addEventListener('click', handleMessageSend);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleMessageSend();
        }
    });
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

// Sidebar Toggle
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    const mainContent = document.querySelector('.chat-main');
    if (sidebar && mainContent) {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    }
}

// Rest of the existing code (message handling, topic management, etc.) remains unchanged...
