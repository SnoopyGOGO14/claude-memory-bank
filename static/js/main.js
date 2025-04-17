// Agent Interface Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // UI Elements
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const agentList = document.getElementById('agent-list');
    const chatHeader = document.getElementById('chat-header');
    
    // State
    let selectedAgent = null;
    let chatHistory = [];
    
    // Load available agents
    loadAgents();
    
    // Add event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
            e.preventDefault();
        }
    });
    
    /**
     * Load the list of available agents from the API
     */
    function loadAgents() {
        fetch('/api/agents')
            .then(response => response.json())
            .then(agents => {
                if (agents.length === 0) {
                    const noAgentMsg = document.createElement('div');
                    noAgentMsg.className = 'alert alert-warning';
                    noAgentMsg.textContent = 'No agents available. Please check the server configuration.';
                    agentList.appendChild(noAgentMsg);
                    return;
                }
                
                // Create agent list items
                agents.forEach(agent => {
                    const agentItem = document.createElement('div');
                    agentItem.className = 'agent-item';
                    agentItem.textContent = agent;
                    agentItem.dataset.agent = agent;
                    
                    agentItem.addEventListener('click', function() {
                        selectAgent(agent);
                        
                        // Update UI - remove active class from all items
                        document.querySelectorAll('.agent-item').forEach(item => {
                            item.classList.remove('active');
                        });
                        
                        // Add active class to selected agent
                        this.classList.add('active');
                    });
                    
                    agentList.appendChild(agentItem);
                });
                
                // Select the first agent by default
                if (agents.length > 0) {
                    selectAgent(agents[0]);
                    document.querySelector('.agent-item').classList.add('active');
                }
            })
            .catch(error => {
                console.error('Error loading agents:', error);
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-danger';
                errorMsg.textContent = 'Failed to load agents. Please check your connection and refresh.';
                agentList.appendChild(errorMsg);
            });
    }
    
    /**
     * Select an agent and update the UI
     */
    function selectAgent(agent) {
        selectedAgent = agent;
        chatHeader.textContent = `Chat with ${agent}`;
        chatMessages.innerHTML = '';
        chatHistory = [];
        
        // Enable input and send button
        messageInput.disabled = false;
        sendButton.disabled = false;
        
        messageInput.focus();
        
        // Add a welcome message
        addAgentMessage(`Hi, I'm ${agent}. How can I assist you today?`);
    }
    
    /**
     * Send a message to the selected agent
     */
    function sendMessage() {
        const message = messageInput.value.trim();
        
        if (!message || !selectedAgent) {
            return;
        }
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input field
        messageInput.value = '';
        
        // Disable send button and show loading state
        sendButton.disabled = true;
        const originalButtonText = sendButton.innerHTML;
        sendButton.innerHTML = '<span class="spinner-border" role="status" aria-hidden="true"></span> Sending...';
        
        // Send request to server
        fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent: selectedAgent,
                command: message
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Unknown error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            // Add agent response to chat
            addAgentMessage(data.response);
        })
        .catch(error => {
            console.error('Error:', error);
            // Show error message in chat
            const errorMessage = document.createElement('div');
            errorMessage.className = 'message agent-message error';
            errorMessage.textContent = `Error: ${error.message || 'Failed to get response'}`;
            chatMessages.appendChild(errorMessage);
        })
        .finally(() => {
            // Restore send button state
            sendButton.disabled = false;
            sendButton.innerHTML = originalButtonText;
            messageInput.focus();
        });
    }
    
    /**
     * Add a user message to the chat interface
     */
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        
        // Save to chat history
        chatHistory.push({ role: 'user', content: message });
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Add an agent message to the chat interface
     */
    function addAgentMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message agent-message';
        
        // Check if message contains code blocks
        if (message.includes('```')) {
            // Process code blocks
            messageElement.innerHTML = processCodeBlocks(message);
        } else {
            // Regular text message
            messageElement.textContent = message;
        }
        
        chatMessages.appendChild(messageElement);
        
        // Save to chat history
        chatHistory.push({ role: 'agent', content: message });
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Process code blocks in messages
     */
    function processCodeBlocks(text) {
        // Replace code blocks with formatted HTML
        let formatted = text.replace(/```([\s\S]*?)```/g, function(match, code) {
            return `<pre><code>${escapeHtml(code)}</code></pre>`;
        });
        
        // Replace single line code with inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Replace newlines with <br> tags
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    /**
     * Escape HTML special characters
     */
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}); 