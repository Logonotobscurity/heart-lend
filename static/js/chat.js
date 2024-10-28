let currentThread = null;
let selectedTopic = null;
let excludedPersonas = new Set();
let availablePersonas = [
    "Ori Sage", "Techno Sage", "Musa the Storyweaver", 
    "Kara the Visionary Dreamer", "Zen Master Kōan",
    "Quantum Observer", "Existential Explorer", "Ethics Guardian"
];
let currentPersonaIndex = 0;
let touchStartX = 0;
let touchEndX = 0;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    const topicsList = document.getElementById('topics-list');
    const activeTopics = document.getElementById('active-topics');
    
    initializeTouchEvents();
    loadTopics();
    
    document.querySelectorAll('[data-role]').forEach(element => {
        element.addEventListener('click', function() {
            const role = this.dataset.role;
            togglePersona(role, this);
        });
    });
    
    function getNextPersona() {
        const activePersonas = availablePersonas.filter(p => !excludedPersonas.has(p));
        if (activePersonas.length === 0) return availablePersonas[0];
        currentPersonaIndex = (currentPersonaIndex + 1) % activePersonas.length;
        return activePersonas[currentPersonaIndex];
    }
    
    function togglePersona(role, element) {
        if (excludedPersonas.has(role)) {
            excludedPersonas.delete(role);
            element.classList.remove('excluded');
            document.querySelectorAll(`[data-role="${role}"]`).forEach(el => {
                el.classList.remove('excluded');
            });
        } else {
            excludedPersonas.add(role);
            element.classList.add('excluded');
            document.querySelectorAll(`[data-role="${role}"]`).forEach(el => {
                el.classList.add('excluded');
            });
        }
    }
    
    async function fetchWithRetry(url, options, retries = MAX_RETRIES) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.status === "error") {
                throw new Error(data.message || "Server error");
            }
            return data;
        } catch (error) {
            if (retries > 0) {
                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                return fetchWithRetry(url, options, retries - 1);
            }
            throw error;
        }
    }
    
    async function loadTopics() {
        try {
            const topics = await fetchWithRetry('/api/topics', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'}
            });
            updateTopicsList(topics);
        } catch (error) {
            console.error('Error loading topics:', error);
            appendSystemMessage('Failed to load topics. Please refresh the page to try again.');
        }
    }
    
    async function suggestTopics(context) {
        try {
            const data = await fetchWithRetry('/api/topics/suggest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ context })
            });
            updateTopicsList(data.topics);
        } catch (error) {
            console.error('Error suggesting topics:', error);
            throw error;
        }
    }
    
    function updateTopicsList(topics) {
        if (topicsList) {
            topicsList.innerHTML = topics.map(topic => `
                <button class="list-group-item list-group-item-action" data-topic-id="${topic.id}">
                    <h6 class="mb-1">${topic.title}</h6>
                    <small class="text-muted">${topic.category}</small>
                    <p class="mb-1 small">${topic.description}</p>
                </button>
            `).join('');
        }
        
        if (activeTopics) {
            activeTopics.innerHTML = topics.map(topic => `
                <div class="topic-chip" data-topic-id="${topic.id}">
                    ${topic.title}
                </div>
            `).join('');
        }
        
        document.querySelectorAll('[data-topic-id]').forEach(button => {
            button.addEventListener('click', function() {
                const topicId = this.dataset.topicId;
                selectTopic(topicId, this);
            });
        });
    }
    
    function selectTopic(topicId, element) {
        selectedTopic = topicId;
        document.querySelectorAll('[data-topic-id]').forEach(el => {
            el.classList.remove('active');
            if (el.dataset.topicId === topicId) {
                el.classList.add('active');
            }
        });
        
        if (!currentThread) {
            messageInput.placeholder = `Start a conversation about: ${element.querySelector('h6')?.textContent || element.textContent}`;
        }
    }
    
    function initializeTouchEvents() {
        const scrollContainers = document.querySelectorAll('.personas-scroll, .topics-scroll');
        
        scrollContainers.forEach(container => {
            container.addEventListener('touchstart', e => {
                touchStartX = e.touches[0].clientX;
            }, false);
            
            container.addEventListener('touchmove', e => {
                if (!touchStartX) return;
                const touchX = e.touches[0].clientX;
                const diff = touchStartX - touchX;
                container.scrollLeft += diff;
                touchStartX = touchX;
            }, false);
            
            container.addEventListener('touchend', () => {
                touchStartX = 0;
            }, false);
        });
    }

    sendButton.addEventListener('click', async function() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        try {
            appendMessage('User', message);
            messageInput.value = '';
            
            const activeRole = getNextPersona();
            
            if (!currentThread) {
                const data = await fetchWithRetry('/api/start_dialogue', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        role: activeRole,
                        context: message,
                        topic_id: selectedTopic
                    })
                });
                
                currentThread = data.thread_id;
                appendMessage(activeRole, data.response);
                
                suggestTopics(message).catch(error => {
                    console.error('Error suggesting topics:', error);
                    appendSystemMessage('Failed to load topic suggestions. The conversation will continue without them.');
                });
                
            } else {
                const data = await fetchWithRetry('/api/continue_dialogue', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        thread_id: currentThread,
                        role: activeRole,
                        message: message
                    })
                });
                
                appendMessage(activeRole, data.response);
            }
        } catch (error) {
            console.error('Error:', error);
            appendSystemMessage(`An error occurred: ${error.message}. Please try again.`);
            
            if (!currentThread) {
                currentThread = null;
            }
        } finally {
            messageInput.disabled = false;
            sendButton.disabled = false;
        }
    });
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });
    
    function appendMessage(role, content) {
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
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-system';
        messageDiv.innerHTML = `
            <strong>System:</strong>
            <p class="text-danger">${content}</p>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});