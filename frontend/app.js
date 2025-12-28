const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const quickActions = document.querySelectorAll('.quick-action');

let history = [];

// Update connection status
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const statusText = statusElement.querySelector('.status-text');
    
    if (connected) {
        statusElement.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusElement.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Show/hide typing indicator
function showTypingIndicator(show) {
    const typingIndicator = document.getElementById('typing-indicator');
    typingIndicator.classList.toggle('hidden', !show);
}

// Add message to chat
function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);
    
    const time = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const icon = role === 'bot' ? '🤖' : '👤';
    const sender = role === 'bot' ? 'Concierge' : 'You';
    
    messageDiv.innerHTML = `
        <div class="message-icon">${icon}</div>
        <div class="message-content">
            <div class="message-sender">${sender}</div>
            <div class="message-text">${formatMessage(content)}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message with line breaks
function formatMessage(text) {
    return text.replace(/\n/g, '<br>');
}

// Setup quick action buttons
function setupQuickActions() {
    quickActions.forEach(button => {
        button.addEventListener('click', () => {
            const prompt = button.getAttribute('data-prompt');
            userInput.value = prompt;
            sendMessage();
        });
    });
}

// Send message to backend
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, 'user');
    userInput.value = '';
    
    // Add to history
    history.push({ role: "user", content: text });

    // Show typing indicator
    showTypingIndicator(true);

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                history: history,
                session_id: 'default'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Add bot response
        addMessage(data.response, 'bot');
        history.push({ role: "assistant", content: data.response });
        
        // Update connection status
        updateConnectionStatus(true);

    } catch (error) {
        console.error('Error:', error);
        addMessage("Sorry, I'm having trouble connecting. Please check if the backend is running.", 'bot');
        updateConnectionStatus(false);
    } finally {
        // Hide typing indicator
        showTypingIndicator(false);
    }
}

// Test backend connection
async function testBackendConnection() {
    try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
            updateConnectionStatus(true);
            console.log('✅ Backend connected');
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        updateConnectionStatus(false);
        console.log('❌ Backend not available');
    }
}

// Setup help example clicks
function setupHelpExamples() {
    document.querySelectorAll('.help-example').forEach(element => {
        element.addEventListener('click', function() {
            const example = this.getAttribute('data-example');
            if (example && userInput) {
                userInput.value = example;
                userInput.focus();
            }
        });
    });
}

// Initialize chat
function initChat() {
    // Setup event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Setup quick actions
    setupQuickActions();
    
    // Setup help examples
    setupHelpExamples();
    
    // Test connection
    testBackendConnection();
    
    // Auto-focus input
    userInput.focus();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initChat);