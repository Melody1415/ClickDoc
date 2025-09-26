// Configuration
const API_BASE_URL = 'http://localhost:5000';
let currentConversationId = generateConversationId();
let chatHistory = [];
let uploadedFiles = [];
let filesAutoLoaded = false;
let filesAddedToConversation = false;

// Generate unique conversation ID
function generateConversationId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Auto-resize textarea
const chatInput = document.getElementById('chatInput');

if (chatInput) {
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('ClickDoc AI Chatbot initialized');
    console.log('Conversation ID:', currentConversationId);
    
    initializeFilesFromServer();
    
    // Focus on input
    if (chatInput) {
        chatInput.focus();
    }
});

// Initialize files from server-side data
function initializeFilesFromServer() {
    // Check if files were passed from the server
    const filesData = window.serverFiles || [];
    if (filesData && filesData.length > 0) {
        uploadedFiles = filesData;
        displayUploadedFiles();
        addFilesToConversation();
        filesAutoLoaded = true;
        console.log(`Loaded ${filesData.length} files from server`);
    } else {
        // Fallback to loading from API
        loadUploadedFiles();
    }
}

// Load uploaded files from API
async function loadUploadedFiles() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/get_files`);
        if (response.ok) {
            const data = await response.json();
            uploadedFiles = data.files || [];
            displayUploadedFiles();
            
            if (uploadedFiles.length > 0 && !filesAutoLoaded) {
                addFilesToConversation();
                filesAutoLoaded = true;
            }
        }
    } catch (error) {
        console.error('Error loading files:', error);
    }
}

// Display uploaded files in sidebar - Clean version
function displayUploadedFiles() {
    const fileSection = document.querySelector('#uploadedFiles');
    if (!fileSection) return;

    fileSection.innerHTML = '';

    if (uploadedFiles.length === 0) {
        fileSection.innerHTML = `
            <li class="file-item">
                <div class="file-icon">📭</div>
                <div class="file-name">No files uploaded yet</div>
            </li>
        `;
        return;
    }

    uploadedFiles.forEach((file, index) => {
        const fileItem = document.createElement('li');
        fileItem.className = 'file-item loaded';
        fileItem.setAttribute('data-filename', file.name);
        fileItem.setAttribute('data-index', index);
        
        const extension = file.name.split('.').pop().toLowerCase();
        const icon = getFileIcon(extension);
        
        fileItem.innerHTML = `
            <div class="file-icon">${icon}</div>
            <div class="file-name">${file.name}</div>
        `;
        
        fileSection.appendChild(fileItem);
    });
}

// Get appropriate file icon
function getFileIcon(extension) {
    const icons = {
        'py': '🐍',
        'js': '⚡',
        'jsx': '⚛️',
        'ts': '🔷',
        'tsx': '🔷',
        'java': '☕',
        'cpp': '🔧',
        'c': '🔨',
        'cs': '🎮',
        'html': '🌐',
        'css': '🎨',
        'scss': '🎨',
        'lua': '🌙'
    };
    return icons[extension.toLowerCase()] || '📄';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Add files to conversation automatically with enhanced welcome message
function addFilesToConversation() {
    if (filesAddedToConversation || uploadedFiles.length === 0) return;
    
    const chatArea = document.querySelector('.chat-area');
    
    // Hide initial prompt elements
    const botAvatar = document.querySelector('.bot-avatar');
    const conversationPrompt = document.querySelector('.conversation-prompt');
    const suggestions = document.querySelector('.suggestions');
    
    if (botAvatar) botAvatar.style.display = 'none';
    if (conversationPrompt) conversationPrompt.style.display = 'none';
    if (suggestions) suggestions.style.display = 'none';
    
    // Remove initial state class
    chatArea.classList.remove('initial-state');
    
    // Add welcome message with files
    const fileNames = uploadedFiles.map(f => f.name);
    
    // Add bot message showing files are loaded
    const welcomeMessage = document.createElement('div');
    welcomeMessage.className = 'message bot-message';
    
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    welcomeMessage.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">🤖</div>
            <span class="message-sender">AI Assistant</span>
        </div>
        <div class="message-content">
            <div class="files-ready-message">
                <div class="files-ready-header">
                    <span class="files-ready-icon">✨</span>
                    <span class="files-ready-title">Files Ready for Analysis!</span>
                </div>
                <div class="files-ready-body">
                    <p>I've successfully loaded ${uploadedFiles.length} file(s) and I'm ready to help you understand the code:</p>
                    <div class="loaded-files-container">
                        ${uploadedFiles.map(file => `
                            <div class="loaded-file-item">
                                <span class="file-icon">${getFileIcon(file.name.split('.').pop())}</span>
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${formatFileSize(file.content?.length || 0)}</span>
                            </div>
                        `).join('')}
                    </div>
                    <p class="ready-prompt">You can ask me to:</p>
                    <ul class="capability-list">
                        <li>📖 Explain what any file does</li>
                        <li>🔍 Analyze the code structure</li>
                        <li>🐛 Find potential issues or bugs</li>
                        <li>💡 Suggest improvements</li>
                        <li>❓ Answer any specific questions about the code</li>
                    </ul>
                    <p class="start-prompt">What would you like to know about your code?</p>
                </div>
            </div>
        </div>
        <div class="message-time">${currentTime}</div>
    `;
    
    chatArea.appendChild(welcomeMessage);
    
    // Scroll to bottom
    chatArea.scrollTop = chatArea.scrollHeight;
    
    filesAddedToConversation = true;
}

// Send message function with enhanced file context
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message with files context
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_id: currentConversationId,
                include_all_files: true,
                selected_files: uploadedFiles.map(f => f.name)
            })
        });
        
        hideTypingIndicator();
        
        if (response.ok) {
            const data = await response.json();
            addMessageToChat('bot', data.response);
        } else {
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        hideTypingIndicator();
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, I couldn\'t connect to the server. Please try again.');
    }
}

// Add message to chat display with enhanced styling
function addMessageToChat(sender, message) {
    const chatArea = document.querySelector('.chat-area');
    
    // Hide initial elements if this is first message
    if (sender === 'user' && !filesAddedToConversation) {
        hideInitialPrompt();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
    
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${currentTime}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar">🤖</div>
                <span class="message-sender">AI Assistant</span>
            </div>
            <div class="message-content">${message}</div>
            <div class="message-time">${currentTime}</div>
        `;
    }
    
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Hide initial prompt elements
function hideInitialPrompt() {
    const botAvatar = document.querySelector('.bot-avatar');
    const conversationPrompt = document.querySelector('.conversation-prompt');
    const suggestions = document.querySelector('.suggestions');

    if (botAvatar) botAvatar.style.display = 'none';
    if (conversationPrompt) conversationPrompt.style.display = 'none';
    if (suggestions) suggestions.style.display = 'none';
    
    // Remove initial state styling
    const chatArea = document.querySelector('.chat-area');
    chatArea.classList.remove('initial-state');
}

// Show typing indicator
function showTypingIndicator() {
    const chatArea = document.querySelector('.chat-area');
    const indicator = document.createElement('div');
    indicator.className = 'message bot-message typing-indicator';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">🤖</div>
            <span class="message-sender">AI Assistant</span>
        </div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatArea.appendChild(indicator);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Handle Enter key in chat input
if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// New conversation function
function startNewConversation() {
    if (confirm('Are you sure you want to start a new conversation? Current chat history will be cleared.')) {
        currentConversationId = generateConversationId();
        const chatArea = document.querySelector('.chat-area');
        
        // Clear all messages
        const messages = chatArea.querySelectorAll('.message');
        messages.forEach(msg => msg.remove());
        
        // Reset conversation state
        filesAddedToConversation = false;
        
        // Re-add files to conversation if they exist
        if (uploadedFiles.length > 0) {
            addFilesToConversation();
        } else {
            // Show initial state if no files
            const botAvatar = document.querySelector('.bot-avatar');
            const conversationPrompt = document.querySelector('.conversation-prompt');
            const suggestions = document.querySelector('.suggestions');

            if (botAvatar) {
                botAvatar.style.display = 'flex';
                conversationPrompt.textContent = 'Start a conversation about your code...';
            }
            if (conversationPrompt) conversationPrompt.style.display = 'block';
            if (suggestions) suggestions.style.display = 'block';
            
            chatArea.classList.add('initial-state');
        }
    }
}

// Utility function to check backend connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            console.log('✅ Backend connected successfully');
            return true;
        }
    } catch (error) {
        console.warn('❌ Backend not connected:', error.message);
        console.warn('Make sure your Flask server is running on http://localhost:5000');
        return false;
    }
}