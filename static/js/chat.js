let activeRole = null;
let currentThread = null;

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    
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
                        context: message
                    })
                });
                const data = await response.json();
                currentThread = data.thread_id;
                appendMessage(activeRole, data.response);
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
