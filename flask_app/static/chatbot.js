const API_BASE_URL = 'http://localhost:5000';
let currentConversationId = generateConversationId();
let chatHistory = [];
let uploadedFiles = [];
let filesAutoLoaded = false;
let filesAddedToConversation = false;

function generateConversationId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

const chatInput = document.getElementById('chat-input');
if (chatInput) {
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('ClickDoc AI Chatbot initialized');
    console.log('Conversation ID:', currentConversationId);
    lucide.createIcons();
    initializeFilesFromServer();
    setupFileUpload();
    if (chatInput) chatInput.focus();
});

function initializeFilesFromServer() {
    const storedFiles = sessionStorage.getItem('uploadedFiles');
    if (storedFiles) {
        uploadedFiles = JSON.parse(storedFiles);
        displayUploadedFiles();
        addFilesToConversation();
        filesAutoLoaded = true;
        console.log(`Loaded ${uploadedFiles.length} files from sessionStorage`);
        syncFilesWithBackend();
    } else {
        const filesData = window.serverFiles || [];
        if (filesData && filesData.length > 0) {
            uploadedFiles = filesData.map(file => ({
                name: file.name,
                size: file.content?.length || 0,
                content: file.content,
                type: file.type || 'text/plain',
                lastModified: file.lastModified || new Date().getTime(),
                uploadedAt: new Date().toISOString()
            }));
            sessionStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));
            displayUploadedFiles();
            addFilesToConversation();
            filesAutoLoaded = true;
            console.log(`Loaded ${filesData.length} files from server`);
            syncFilesWithBackend();
        } else {
            loadUploadedFiles();
        }
    }
}

async function loadUploadedFiles() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/get_files`);
        if (response.ok) {
            const data = await response.json();
            uploadedFiles = (data.files || []).map(file => ({
                name: file.name,
                size: file.content?.length || 0,
                content: file.content,
                type: file.type || 'text/plain',
                lastModified: file.lastModified || new Date().getTime(),
                uploadedAt: new Date().toISOString()
            }));
            sessionStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));
            displayUploadedFiles();
            if (uploadedFiles.length > 0 && !filesAutoLoaded) {
                addFilesToConversation();
                filesAutoLoaded = true;
            }
            syncFilesWithBackend();
        }
    } catch (error) {
        console.error('Error loading files:', error);
        displayUploadedFiles();
    }
}

async function syncFilesWithBackend() {
    try {
        const validFiles = uploadedFiles.filter(f => f.content && f.content.trim());
        if (validFiles.length === 0) {
            console.log('No valid files to sync with backend');
            return;
        }
        const response = await fetch(`${API_BASE_URL}/api/set_files`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: validFiles.map(f => ({ name: f.name, content: btoa(f.content), type: f.type })) })
        });
        if (response.ok) {
            console.log(`Synced ${validFiles.length} files with backend`);
        } else {
            console.error('Failed to sync files with backend:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error syncing files:', error);
    }
}

function displayUploadedFiles() {
    const fileSection = document.getElementById('uploaded-files');
    if (!fileSection) return;

    fileSection.innerHTML = '';

    if (uploadedFiles.length === 0) {
        fileSection.innerHTML = `
            <div class="text-center py-6">
                <i data-lucide="folder-x" class="w-8 h-8 text-gray-400 mx-auto mb-2"></i>
                <p class="text-gray-500 text-sm">No files uploaded</p>
                <button onclick="document.getElementById('file-input').click()" class="text-blue-600 hover:text-blue-800 text-sm mt-2">Upload Files</button>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    uploadedFiles.forEach((file, index) => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'flex items-center gap-3 p-3 bg-gray-50 rounded-lg group';
        fileDiv.innerHTML = `
            <i data-lucide="${getFileIcon(file.name)}" class="w-5 h-5 ${getFileIconColor(file.name)}"></i>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">${file.name}</p>
                <p class="text-xs text-gray-500">${formatFileSize(file.size)}</p>
            </div>
            <button onclick="removeFile(${index})" class="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        `;
        fileSection.appendChild(fileDiv);
    });
    lucide.createIcons();
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'js': 'file-code', 'jsx': 'file-code', 'ts': 'file-code', 'tsx': 'file-code',
        'html': 'file-text', 'css': 'file-text', 'json': 'file-text',
        'py': 'file-code', 'java': 'file-code', 'c': 'file-code', 'cpp': 'file-code', 'h': 'file-code',
        'cs': 'file-code', 'php': 'file-code', 'rb': 'file-code', 'go': 'file-code', 'rs': 'file-code',
        'swift': 'file-code', 'kt': 'file-code',
        'xml': 'file-text', 'yml': 'file-text', 'yaml': 'file-text', 'properties': 'file-text',
        'sh': 'terminal', 'bash': 'terminal', 'sql': 'database',
        'md': 'file-text', 'r': 'file-code', 'scala': 'file-code', 'dart': 'file-code'
    };
    return iconMap[ext] || 'file';
}

function getFileIconColor(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const colorMap = {
        'js': 'text-yellow-600', 'jsx': 'text-yellow-600', 'ts': 'text-blue-600', 'tsx': 'text-blue-600',
        'html': 'text-red-600', 'css': 'text-purple-600', 'json': 'text-gray-600',
        'py': 'text-green-600', 'java': 'text-orange-600', 'c': 'text-blue-500', 'cpp': 'text-blue-500', 'h': 'text-blue-500',
        'cs': 'text-purple-500', 'php': 'text-indigo-600', 'rb': 'text-red-500', 'go': 'text-cyan-600', 'rs': 'text-orange-500',
        'swift': 'text-orange-400', 'kt': 'text-purple-400',
        'xml': 'text-green-500', 'yml': 'text-purple-500', 'yaml': 'text-purple-500', 'properties': 'text-gray-500',
        'sh': 'text-green-700', 'bash': 'text-green-700', 'sql': 'text-blue-700',
        'md': 'text-blue-500', 'r': 'text-blue-400', 'scala': 'text-red-400', 'dart': 'text-blue-400'
    };
    return colorMap[ext] || 'text-gray-500';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function setupFileUpload() {
    const uploadMoreBtn = document.getElementById('upload-more-btn');
    const fileInput = document.getElementById('file-input');
    const sidebar = document.querySelector('.w-80');

    if (uploadMoreBtn && fileInput) {
        uploadMoreBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(Array.from(e.target.files));
                e.target.value = '';
            }
        });
    }

    if (sidebar) {
        sidebar.addEventListener('dragover', (e) => {
            e.preventDefault();
            sidebar.classList.add('bg-blue-50', 'border-blue-300');
        });
        sidebar.addEventListener('dragleave', (e) => {
            e.preventDefault();
            sidebar.classList.remove('bg-blue-50', 'border-blue-300');
        });
        sidebar.addEventListener('drop', (e) => {
            e.preventDefault();
            sidebar.classList.remove('bg-blue-50', 'border-blue-300');
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) handleFileUpload(files);
        });
    }
}

async function handleFileUpload(files) {
    const uploadModal = document.getElementById('upload-modal');
    const progressBar = document.getElementById('progress-bar');
    const uploadStatus = document.getElementById('upload-status');

    if (files.length === 0) return;

    const validFiles = [];
    const invalidFiles = [];
    const allowedExtensions = [
        '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.json', '.md',
        '.py', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.rb', '.go', '.rs',
        '.swift', '.kt', '.xml', '.yml', '.yaml', '.properties', '.sh', '.bash',
        '.sql', '.r', '.scala', '.dart'
    ];

    files.forEach(file => {
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (allowedExtensions.includes(fileExt)) validFiles.push(file);
        else invalidFiles.push(file.name);
    });

    if (invalidFiles.length > 0) {
        alert(`❌ The following files are not supported:\n\n${invalidFiles.join('\n')}\n\n✅ Supported file types: ${allowedExtensions.join(', ')}`);
    }

    if (validFiles.length === 0) return;

    uploadModal.classList.remove('hidden');
    const totalFiles = validFiles.length;
    let processedFiles = 0;

    for (const file of validFiles) {
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert(`${file.name} is too large (>10MB). Please upload smaller files.`);
            continue;
        }

        uploadStatus.textContent = `Processing ${file.name}... (${processedFiles + 1}/${totalFiles})`;
        try {
            const content = await readFileContent(file);
            const fileData = {
                name: file.name,
                size: file.size,
                content: content,
                type: file.type,
                lastModified: file.lastModified,
                uploadedAt: new Date().toISOString()
            };

            const existingFileIndex = uploadedFiles.findIndex(f => f.name === file.name);
            if (existingFileIndex !== -1) uploadedFiles[existingFileIndex] = fileData;
            else uploadedFiles.push(fileData);
        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
            alert(`Failed to read ${file.name}: ${error.message}. Skipping this file.`);
            continue;
        }
        processedFiles++;
        progressBar.style.width = `${(processedFiles / totalFiles) * 100}%`;
    }

    sessionStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));
    uploadStatus.textContent = 'Upload completed!';
    await new Promise(resolve => setTimeout(resolve, 500));
    uploadModal.classList.add('hidden');
    displayUploadedFiles();
    addFilesToConversation();
    progressBar.style.width = '0%';
    uploadStatus.textContent = 'Preparing files...';

    await syncFilesWithBackend();
}

async function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            console.log(`Read ${file.name}: ${e.target.result.length} bytes`);
            resolve(e.target.result);
        };
        reader.onerror = (e) => {
            const errorMsg = `Failed to read ${file.name}: ${reader.error?.code || 'Unknown error'}`;
            console.error('FileReader error:', e);
            reject(new Error(errorMsg));
        };
        reader.readAsText(file, 'UTF-8');
    });
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    sessionStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));
    displayUploadedFiles();
    addFilesToConversation();
    syncFilesWithBackend();
}

function addFilesToConversation() {
    if (filesAddedToConversation && uploadedFiles.length > 0) return;
    
    const chatArea = document.getElementById('chat-area');
    const initialState = document.getElementById('initial-state');

    if (initialState) initialState.style.display = 'none';
    chatArea.classList.remove('flex', 'items-center', 'justify-center', 'text-center');

    if (uploadedFiles.length === 0) {
        chatArea.innerHTML = `
            <div id="initial-state" class="flex flex-col items-center justify-center h-full text-center">
                <div class="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mb-6 relative">
                    <span class="text-2xl">🤖</span>
                    <span class="absolute bottom-1 right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
                </div>
                <p class="text-gray-600 text-lg mb-6">No files uploaded. Please upload files to start.</p>
                <div class="text-left text-gray-600">
                    <p class="font-semibold mb-2">I can help you with:</p>
                    <p class="text-sm">• Upload code files to analyze</p>
                    <p class="text-sm">• Ask about code structure</p>
                    <p class="text-sm">• Get help with debugging</p>
                </div>
            </div>
        `;
        return;
    }

    const welcomeMessage = document.createElement('div');
    welcomeMessage.className = 'mb-4';
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    welcomeMessage.innerHTML = `
        <div class="flex gap-2 mb-2">
            <div class="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                <span class="text-white text-sm">🤖</span>
            </div>
            <span class="text-gray-800 font-semibold">AI Assistant</span>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div class="flex items-center gap-2 mb-4">
                <i data-lucide="sparkles" class="w-6 h-6 text-blue-600"></i>
                <span class="text-lg font-bold text-blue-800">Files Ready for Analysis!</span>
            </div>
            <p class="text-gray-800 mb-4">I've successfully loaded ${uploadedFiles.length} file(s):</p>
            <div class="space-y-2 mb-4">
                ${uploadedFiles.map(file => `
                    <div class="flex items-center gap-3 p-3 bg-white rounded-lg">
                        <i data-lucide="${getFileIcon(file.name)}" class="w-5 h-5 ${getFileIconColor(file.name)}"></i>
                        <span class="text-sm font-medium text-gray-800 truncate flex-1">${file.name}</span>
                        <span class="text-xs text-gray-500">${formatFileSize(file.size)}</span>
                    </div>
                `).join('')}
            </div>
            <p class="text-gray-800 mb-2">You can ask me to:</p>
            <ul class="space-y-2 mb-4">
                <li class="p-2 bg-white rounded-lg border-l-4 border-blue-600 cursor-pointer" onclick="sendPresetMessage('Explain what any file does')">Explain what any file does</li>
                <li class="p-2 bg-white rounded-lg border-l-4 border-blue-600 cursor-pointer" onclick="sendPresetMessage('Analyze the code structure')">Analyze the code structure</li>
                <li class="p-2 bg-white rounded-lg border-l-4 border-blue-600 cursor-pointer" onclick="sendPresetMessage('Find potential issues or bugs')">Find potential issues or bugs</li>
                <li class="p-2 bg-white rounded-lg border-l-4 border-blue-600 cursor-pointer" onclick="sendPresetMessage('Suggest improvements')">Suggest improvements</li>
                <li class="p-2 bg-white rounded-lg border-l-4 border-blue-600 cursor-pointer" onclick="sendPresetMessage('Answer any specific questions about the code')">Answer any specific questions about the code</li>
            </ul>
            <p class="text-gray-800">What would you like to know about your code?</p>
        </div>
        <p class="text-xs text-gray-500 mt-2 text-right">${currentTime}</p>
    `;
    
    chatArea.appendChild(welcomeMessage);
    chatArea.scrollTop = chatArea.scrollHeight;
    lucide.createIcons();
    filesAddedToConversation = true;
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    chatInput.value = '';
    chatInput.style.height = 'auto';
    addMessageToChat('user', message);
    showTypingIndicator();

    try {
        const validFiles = uploadedFiles.filter(f => f.content && f.content.trim());
        if (validFiles.length === 0 && uploadedFiles.length > 0) {
            console.warn('No valid file contents to send');
            addMessageToChat('bot', 'No valid files found. Please upload files with readable content.');
            hideTypingIndicator();
            return;
        }

        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_id: currentConversationId,
                include_all_files: true,
                selected_files: validFiles.map(f => f.name) // Send only filenames, backend uses session
            })
        });

        hideTypingIndicator();
        if (response.ok) {
            const data = await response.json();
            addMessageToChat('bot', data.response);
        } else {
            console.error('Chat request failed:', response.status, response.statusText);
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        hideTypingIndicator();
        console.error('Error in sendMessage:', error);
        addMessageToChat('bot', 'Sorry, I couldn\'t connect to the server. Please try again.');
    }
}

function addMessageToChat(sender, message) {
    const chatArea = document.getElementById('chat-area');
    if (sender === 'user' && !filesAddedToConversation) {
        const initialState = document.getElementById('initial-state');
        if (initialState) initialState.style.display = 'none';
        chatArea.classList.remove('flex', 'items-center', 'justify-center', 'text-center');
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-4 ${sender === 'user' ? 'ml-auto' : ''}`;
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="bg-blue-600 text-white p-4 rounded-lg max-w-[85%] ml-auto rounded-br-none">
                ${message}
            </div>
            <p class="text-xs text-gray-500 mt-2 text-right">${currentTime}</p>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="flex gap-2 mb-2">
                <div class="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                    <span class="text-white text-sm">🤖</span>
                </div>
                <span class="text-gray-800 font-semibold">AI Assistant</span>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 max-w-[85%] rounded-bl-none">
                ${message}
            </div>
            <p class="text-xs text-gray-500 mt-2">${currentTime}</p>
        `;
    }

    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
    lucide.createIcons();
}

function showTypingIndicator() {
    const chatArea = document.getElementById('chat-area');
    const indicator = document.createElement('div');
    indicator.className = 'mb-4';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="flex gap-2 mb-2">
            <div class="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                <span class="text-white text-sm">🤖</span>
            </div>
            <span class="text-gray-800 font-semibold">AI Assistant</span>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 max-w-[85%] rounded-bl-none">
            <div class="flex gap-2">
                <span class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></span>
                <span class="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-200"></span>
                <span class="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-400"></span>
            </div>
        </div>
    `;
    chatArea.appendChild(indicator);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function startNewConversation() {
    if (confirm('Are you sure you want to start a new conversation? Current chat history will be cleared.')) {
        currentConversationId = generateConversationId();
        const chatArea = document.getElementById('chat-area');
        chatArea.innerHTML = '';
        filesAddedToConversation = false;
        addFilesToConversation();
        // Clear conversation on backend
        fetch(`${API_BASE_URL}/api/clear_conversation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conversation_id: currentConversationId })
        }).then(response => {
            if (response.ok) console.log('Conversation cleared on backend');
        }).catch(error => console.error('Error clearing conversation:', error));
    }
}

function sendPresetMessage(message) {
    if (chatInput) {
        chatInput.value = message;
        sendMessage();
    }
}

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