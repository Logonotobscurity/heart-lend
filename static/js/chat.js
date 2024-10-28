let activeRole = null;
let currentThread = null;
let selectedTopic = null;

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    const topicsList = document.getElementById('topics-list');
    
    // Load initial topics
    loadTopics();
    
    // Role selection
    document.querySelectorAll('[data-role]').forEach(button => {
        button.addEventListener('click', function() {
            activeRole = this.dataset.role;
            document.querySelectorAll('[data-role]').forEach(btn => 
                btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Send message
    sendButton.addEventListener('click', async function() {
        if (!activeRole) {
            alert('Please select an AI persona first');
            return;
        }
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        appendMessage('User', message);
        messageInput.value = '';
        
        try {
            if (!currentThread) {
                // Start new dialogue
                const response = await fetch('/api/start_dialogue', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        role: activeRole,
                        context: message,
                        topic_id: selectedTopic
                    })
                });
                const data = await response.json();
                currentThread = data.thread_id;
                appendMessage(activeRole, data.response);
                
                // Request topic suggestions based on the context
                suggestTopics(message);
            } else {
                // Continue dialogue
                const response = await fetch('/api/continue_dialogue', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        thread_id: currentThread,
                        role: activeRole,
                        message: message
                    })
                });
                const data = await response.json();
                appendMessage(activeRole, data.response);
            }
        } catch (error) {
            console.error('Error:', error);
            appendMessage('System', 'An error occurred. Please try again.');
        }
    });
    
    async function loadTopics() {
        try {
            const response = await fetch('/api/topics');
            const topics = await response.json();
            updateTopicsList(topics);
        } catch (error) {
            console.error('Error loading topics:', error);
        }
    }
    
    async function suggestTopics(context) {
        try {
            const response = await fetch('/api/topics/suggest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ context })
            });
            const data = await response.json();
            if (data.status === 'success') {
                updateTopicsList(data.topics);
            }
        } catch (error) {
            console.error('Error suggesting topics:', error);
        }
    }
    
    function updateTopicsList(topics) {
        topicsList.innerHTML = topics.map(topic => `
            <button class="list-group-item list-group-item-action" data-topic-id="${topic.id}">
                <h6 class="mb-1">${topic.title}</h6>
                <small class="text-muted">${topic.category}</small>
                <p class="mb-1 small">${topic.description}</p>
            </button>
        `).join('');
        
        // Add click handlers for topics
        document.querySelectorAll('[data-topic-id]').forEach(button => {
            button.addEventListener('click', function() {
                selectedTopic = this.dataset.topicId;
                document.querySelectorAll('[data-topic-id]').forEach(btn => 
                    btn.classList.remove('active'));
                this.classList.add('active');
                
                if (!currentThread) {
                    messageInput.placeholder = `Start a conversation about: ${this.querySelector('h6').textContent}`;
                }
            });
        });
    }
    
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
});
