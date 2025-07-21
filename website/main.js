class ChatApp {
    constructor() {
        // Determine API base URL (use localhost server when opened via file://)
        this.apiURL = window.location.protocol === 'file:'
            ? 'http://localhost:5000'
            : window.location.origin;
        this.chats = [];
        this.currentChatId = 1;
        this.selectedTools = new Set();
        this.messageId = 0;
        this.isGenerating = false;
        this.isPaused = false;
        this.generationTimeout = null;
        this.isNewChat = true;
        
        this.initializeElements();
        this.attachEventListeners();
        
        // Load available tools from backend on startup
        this.loadAvailableTools();
        this.setupAutoResize();

        // Restore selected tools from cookies
        this.restoreSelectedToolsFromCookies();
        // Show selected tools below input bar on load
        this.updateSelectedToolsDisplay();
    }
    // Cookie helpers
    setCookie(name, value, days = 365) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
    }

    getCookie(name) {
        return document.cookie.split('; ').reduce((r, v) => {
            const parts = v.split('=');
            return parts[0] === name ? decodeURIComponent(parts[1]) : r;
        }, '');
    }

    saveSelectedToolsToCookies() {
        this.setCookie('selectedTools', JSON.stringify(Array.from(this.selectedTools)));
    }

    restoreSelectedToolsFromCookies() {
        const cookie = this.getCookie('selectedTools');
        if (cookie) {
            try {
                const arr = JSON.parse(cookie);
                if (Array.isArray(arr)) {
                    this.selectedTools = new Set(arr);
                }
            } catch (e) {}
        }
    }
    
    initializeElements() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.toolBtn = document.getElementById('toolBtn');
        this.toolModal = document.getElementById('toolModal');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.chatHistory = document.getElementById('chatHistory');
        this.selectedToolsContainer = document.getElementById('selectedTools');
        this.closeModal = document.getElementById('closeModal');
        this.applyTools = document.getElementById('applyTools');
        this.clearTools = document.getElementById('clearTools');

        // New elements
        this.pauseBtn = document.getElementById('pauseBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.inputArea = document.querySelector('.input-area');
        this.userAvatar = document.querySelector('.user-avatar');
        this.userMenu = document.getElementById('userMenu');

        // Theme toggle
        this.themeSwitch = document.getElementById('themeSwitch');

        // Sidebar toggle
        this.toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
        this.sidebar = document.querySelector('.sidebar');
        // Collapse sidebar by default, and prevent animation on load
        if (this.sidebar) {
            this.sidebar.classList.add('collapsed');
            // Remove transition for initial load
            this.sidebar.classList.remove('enable-transition');
            // Enable transition after a short delay (next tick)
            setTimeout(() => {
                this.sidebar.classList.add('enable-transition');
            }, 50);
        }

        // Title bar controls
        this.minimizeBtn = document.getElementById('minimizeBtn');
        this.maximizeBtn = document.getElementById('maximizeBtn');
        this.closeBtn = document.getElementById('closeBtn');

        // Prevent menu from closing when clicking theme toggle
        const themeToggleItem = document.querySelector('.user-menu-item .theme-toggle');
        if (themeToggleItem) {
            themeToggleItem.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Initialize with centered input for new chat
        this.inputArea.classList.add('centered');

        // Initialize theme
        this.initializeTheme();
    }
    
    attachEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.toolBtn.addEventListener('click', () => this.openToolModal());
        this.closeModal.addEventListener('click', () => this.closeToolModal());
        this.toolModal.addEventListener('click', (e) => {
            if (e.target === this.toolModal) {
                this.closeToolModal();
            }
        });
        
        this.applyTools.addEventListener('click', () => this.applySelectedTools());
        this.clearTools.addEventListener('click', () => this.clearSelectedTools());
        
        this.newChatBtn.addEventListener('click', () => this.createNewChat());
        
        // Generation control buttons
        this.pauseBtn.addEventListener('click', () => this.pauseGeneration());
        this.stopBtn.addEventListener('click', () => this.stopGeneration());
        
        // User menu
        this.userAvatar.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleUserMenu();
        });
        
        // Close user menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.userAvatar.contains(e.target)) {
                this.userMenu.classList.remove('active');
            }
        });
        
        // Tool selection listeners
        const toolCheckboxes = document.querySelectorAll('input[type="checkbox"][data-tool]');
        toolCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateToolSelection());
        });
        
        // Sidebar toggle
        this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
        
        // Title bar controls
        this.minimizeBtn.addEventListener('click', () => this.minimizeWindow());
        this.maximizeBtn.addEventListener('click', () => this.maximizeWindow());
        this.closeBtn.addEventListener('click', () => this.closeWindow());
    }
    
    toggleUserMenu() {
        this.userMenu.classList.toggle('active');
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('collapsed');
        // Update the arrow direction
        const arrow = this.toggleSidebarBtn.querySelector('svg polyline');
        if (this.sidebar.classList.contains('collapsed')) {
            arrow.setAttribute('points', '9 18 15 12 9 6'); // Point right
        } else {
            arrow.setAttribute('points', '15 18 9 12 15 6'); // Point left
        }
    }
    
    // Window control methods
    minimizeWindow() {
        // Send message to Electron main process to minimize window
        if (window.electronAPI) {
            window.electronAPI.minimize();
        } else {
            // Fallback for development/browser environment
            console.log('Minimize window (Electron not available)');
        }
    }
    
    maximizeWindow() {
        // Send message to Electron main process to maximize/restore window
        if (window.electronAPI) {
            window.electronAPI.maximize();
        } else {
            // Fallback for development/browser environment
            console.log('Maximize window (Electron not available)');
        }
    }
    
    closeWindow() {
        // Send message to Electron main process to close window
        if (window.electronAPI) {
            window.electronAPI.close();
        } else {
            // Fallback for development/browser environment
            console.log('Close window (Electron not available)');
        }
    }
    
    setupAutoResize() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }

    // Theme initialization: apply saved theme and set up toggle listener
    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            this.themeSwitch.classList.add('active');
        } else {
            document.documentElement.removeAttribute('data-theme');
            this.themeSwitch.classList.remove('active');
        }
        this.themeSwitch.addEventListener('click', () => {
            if (document.documentElement.getAttribute('data-theme') === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                this.themeSwitch.classList.remove('active');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                this.themeSwitch.classList.add('active');
                localStorage.setItem('theme', 'dark');
            }
        });
    }
    
    // Fetch available tools from the backend and render in modal
    loadAvailableTools() {
        fetch(`${this.apiURL}/tools`)
            .then(res => res.json())
            .then(data => {
                // Filter out always-on tools from UI
                const alwaysOn = ['main.speak', 'main.stop', 'main.memory'];
                this.availableTools = (data.tools || []).filter(tool => !alwaysOn.includes(tool.name));
                this.renderToolOptions();
            })
            .catch(err => console.error('Failed to load tools', err));
    }

    // Render dynamic tool selection options
    renderToolOptions() {
        const modalBody = this.toolModal.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="tool-category">
                <h4>Available Tools</h4>
                <div class="tool-list" id="dynamicToolList"></div>
            </div>
        `;
        const toolList = modalBody.querySelector('#dynamicToolList');
        this.availableTools.forEach(tool => {
            const label = document.createElement('label');
            label.className = 'tool-option';
            label.innerHTML = `
                <input type="checkbox" data-tool="${tool.name}">
                <div class="tool-info">
                    <div class="tool-name">${tool.name}</div>
                    <div class="tool-description">${tool.description}</div>
                </div>
            `;
            toolList.appendChild(label);
        });
        // Re-attach checkbox listeners
        const toolCheckboxes = modalBody.querySelectorAll('input[type="checkbox"][data-tool]');
        toolCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateToolSelection());
            // Restore checked state from cookies
            if (this.selectedTools.has(checkbox.dataset.tool)) {
                checkbox.checked = true;
            }
        });
    }

    sendMessage() {
        if (this.isGenerating) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Move input to bottom if this is the first message
        if (this.isNewChat) {
            this.inputArea.classList.remove('centered');
            this.isNewChat = false;
        }
        
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        this.startGeneration();
        // Call backend chat endpoint
        // Collect selected tools as array, always include always-on tools
        const alwaysOn = ['main.speak', 'main.stop', 'main.memory'];
        const selectedTools = Array.from(new Set([...this.selectedTools, ...alwaysOn]));
        fetch(`${this.apiURL}/api/stream-chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: message, selected_tools: selectedTools })
        })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            const processChunk = ({ done, value }) => {
                if (done) {
                    this.stopGeneration();
                    return;
                }
                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n\n');
                buffer = parts.pop();
                parts.forEach(part => {
                    const lines = part.split('\n');
                    const event = lines[0].replace('event: ', '');
                    const data = JSON.parse(lines[1].replace('data: ', ''));
                    // if (event === 'ai_response') {
                    //     this.addMessage(data.text, 'assistant');
                    if (event === 'tool_result') {
                        // Only output main.speak tool results
                        if (data.name === 'main.speak') {
                            const content = data.success ?
                                `${data.result}` :
                                `❌ ${data.name} failed: ${data.error}`;
                            this.addMessage(content, 'assistant');
                        } else if (data.name === 'main.stop') {
                        } else {
                            this.addMessageTool({
                                toolName: data.name || 'Tool',
                                result: data.success ? (data.result || 'Success') : (data.error || 'Error'),
                                success: !!data.success,
                                details: data.details || ''
                            }, 'assistant');
                        }
                    } else if (event === 'done') {
                        this.stopGeneration();
                        if (data.stop) {
                            // Optionally indicate completion
                        }
                    }
        
                });
                return reader.read().then(processChunk);
            };
            return reader.read().then(processChunk);
        })
        .catch(err => {
            this.stopGeneration();
            this.addMessage(`Error: ${err.toString()}`, 'assistant');
        });
    }
    
    startGeneration() {
        this.isGenerating = true;
        this.isPaused = false;
        
        // Hide send button, show pause and stop buttons
        this.sendBtn.style.display = 'none';
        this.pauseBtn.style.display = 'flex';
        this.stopBtn.style.display = 'flex';
    }
    
    pauseGeneration() {
        if (this.isPaused) {
            // Resume
            this.isPaused = false;
            this.pauseBtn.classList.remove('paused');
            this.pauseBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="6" y="4" width="4" height="16"/>
                    <rect x="14" y="4" width="4" height="16"/>
                </svg>
            `;
        } else {
            // Pause
            this.isPaused = true;
            this.pauseBtn.classList.add('paused');
            this.pauseBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5,3 19,12 5,21"/>
                </svg>
            `;
            
            if (this.generationTimeout) {
                clearTimeout(this.generationTimeout);
                this.generationTimeout = null;
            }
        }
    }
    
    stopGeneration() {
        this.isGenerating = false;
        this.isPaused = false;
        
        if (this.generationTimeout) {
            clearTimeout(this.generationTimeout);
            this.generationTimeout = null;
        }
        
        // Show send button, hide pause and stop buttons
        this.sendBtn.style.display = 'flex';
        this.pauseBtn.style.display = 'none';
        this.stopBtn.style.display = 'none';
        this.pauseBtn.classList.remove('paused');
        
        // Reset pause button icon
        this.pauseBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
            </svg>
        `;
    }
    
    addMessage(content, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? 
            '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' :
            '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></svg>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = content;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());
        
        messageContent.appendChild(messageText);
        messageContent.appendChild(messageTime);
        
        messageElement.appendChild(avatar);
        messageElement.appendChild(messageContent);
        
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    addMessageTool({ toolName, result, success, details = '' }, sender = 'assistant') {
        // Create a special tool message element
        const messageElement = document.createElement('div');
        messageElement.className = `message tool-message ${sender}`;

        // Tool icon (wrench)
        const toolIcon = document.createElement('div');
        toolIcon.className = 'tool-message-icon';
        toolIcon.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a5 5 0 0 1-6.6 6.6l-4.1 4.1a2 2 0 1 0 2.8 2.8l4.1-4.1a5 5 0 1 1 6.6-6.6z"/></svg>';

        // Tool content
        const messageContent = document.createElement('div');
        messageContent.className = 'tool-message-content';

        // Tool name and status (show only after dot)
        const displayName = toolName.split('.').pop().replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
        const toolHeader = document.createElement('div');
        toolHeader.className = 'tool-message-header';
        toolHeader.innerHTML = `
            <span class="tool-message-toolname">${displayName}</span>
            <span class="tool-message-status" style="color: ${success ? '#2ecc40' : '#ff4136'}; font-size: 1.2em; margin-left: 8px;">${success ? '✔️' : '❌'}</span>
        `;

        // Tool result
        const toolResult = document.createElement('div');
        toolResult.className = 'tool-message-result';
        toolResult.textContent = result;

        // Optional details
        if (details) {
            const toolDetails = document.createElement('div');
            toolDetails.className = 'tool-message-details';
            toolDetails.textContent = details;
            messageContent.appendChild(toolDetails);
        }

        // Time
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());

        messageContent.appendChild(toolHeader);
        messageContent.appendChild(toolResult);
        messageContent.appendChild(messageTime);

        messageElement.appendChild(toolIcon);
        messageElement.appendChild(messageContent);

        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    simulateAIResponse(userMessage) {
        let response = "I understand you're asking about: \"" + userMessage + "\". ";
        
        if (this.selectedTools.size > 0) {
            response += "I'll use the following tools to help you: " + 
                       Array.from(this.selectedTools).map(tool => 
                           tool.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
                       ).join(', ') + ". ";
        }
        
        response += "This is a demo response. In a real implementation, this would be connected to an AI service that would process your request and provide a meaningful response.";
        
        this.addMessage(response, 'assistant');
    }
    
    openToolModal() {
        this.toolModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeToolModal() {
        this.toolModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    updateToolSelection() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][data-tool]');
        this.selectedTools.clear();
        checkboxes.forEach(cb => {
            if (cb.checked) {
                this.selectedTools.add(cb.dataset.tool);
            }
        });
        this.saveSelectedToolsToCookies();
        const selectedCount = this.selectedTools.size;
        if (selectedCount > 0) {
            this.toolBtn.classList.add('active');
        } else {
            this.toolBtn.classList.remove('active');
        }
    }
    
    applySelectedTools() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][data-tool]');
        this.selectedTools.clear();
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                this.selectedTools.add(checkbox.dataset.tool);
            }
        });
        this.saveSelectedToolsToCookies();
        this.updateSelectedToolsDisplay();
        this.closeToolModal();
    }
    
    clearSelectedTools() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][data-tool]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        this.selectedTools.clear();
        this.saveSelectedToolsToCookies();
        this.updateSelectedToolsDisplay();
        this.toolBtn.classList.remove('active');
    }
    
    updateSelectedToolsDisplay() {
        this.selectedToolsContainer.innerHTML = '';
        this.selectedTools.forEach(tool => {
            // Only show the part after the dot (e.g. main.test -> Test)
            const displayName = tool.split('.').pop().replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            const toolTag = document.createElement('div');
            toolTag.className = 'tool-tag';
            toolTag.innerHTML = `
                ${displayName}
                <button onclick="chatApp.removeSelectedTool('${tool}')">×</button>
            `;
            this.selectedToolsContainer.appendChild(toolTag);
        });
    }
    
    removeSelectedTool(tool) {
        this.selectedTools.delete(tool);
        this.saveSelectedToolsToCookies();
        // Update checkbox state
        const checkbox = document.querySelector(`input[data-tool="${tool}"]`);
        if (checkbox) {
            checkbox.checked = false;
        }
        this.updateSelectedToolsDisplay();
        this.updateToolSelection();
    }
    
    createNewChat() {
        // Reset AI context in backend
        fetch(`${this.apiURL}/api/new-chat`, { method: 'POST' })
            .then(res => res.json())
            .then(data => console.log('Backend chat reset:', data))
            .catch(err => console.error('Failed to reset backend chat:', err));
        this.currentChatId++;
        this.isNewChat = true;
        
        // Stop any ongoing generation
        this.stopGeneration();
        
        // Add new chat to history
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.dataset.chatId = this.currentChatId;
        chatItem.innerHTML = `
            <div class="chat-title">New Chat ${this.currentChatId}</div>
            <div class="chat-preview">Start a new conversation</div>
        `;
        
        // Remove active class from other chats
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });
        
        chatItem.classList.add('active');
        this.chatHistory.insertBefore(chatItem, this.chatHistory.firstChild);
        
        // Clear current chat and show centered input
        this.clearChat();
        this.inputArea.classList.add('centered');
        
        // Add click listener
        chatItem.addEventListener('click', () => this.switchChat(this.currentChatId));
    }
    
    switchChat(chatId) {
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const chatItem = document.querySelector(`[data-chat-id="${chatId}"]`);
        if (chatItem) {
            chatItem.classList.add('active');
        }
        
        this.currentChatId = chatId;
        this.isNewChat = true;
        this.clearChat();
        this.inputArea.classList.add('centered');
        this.stopGeneration();
    }
    
    clearChat() {
        this.chatContainer.innerHTML = '';
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('de-DE', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
    // Focus the input bar on load
    const input = document.getElementById('messageInput');
    if (input) input.focus();
});