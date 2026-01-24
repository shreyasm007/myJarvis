/**
 * Portfolio RAG Chatbot Widget
 * 
 * A lightweight, embeddable chat widget for portfolio websites.
 * Supports streaming responses and maintains conversation history.
 * 
 * Usage:
 *   <script src="https://your-api-url/widget/chat-widget.js" 
 *           data-api-url="https://your-api-url"></script>
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        apiUrl: document.currentScript?.getAttribute('data-api-url') || 'http://localhost:8000',
        position: document.currentScript?.getAttribute('data-position') || 'right',
        primaryColor: document.currentScript?.getAttribute('data-primary-color') || '#2563eb',
        title: document.currentScript?.getAttribute('data-title') || 'Chat with Me',
    };

    // Styles
    const STYLES = `
        .rag-chat-widget * {
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }

        .rag-chat-bubble {
            position: fixed;
            bottom: 24px;
            ${CONFIG.position === 'left' ? 'left: 24px;' : 'right: 24px;'}
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: ${CONFIG.primaryColor};
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            z-index: 9999;
        }

        .rag-chat-bubble:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        .rag-chat-bubble svg {
            width: 28px;
            height: 28px;
            fill: white;
        }

        .rag-chat-window {
            position: fixed;
            bottom: 100px;
            ${CONFIG.position === 'left' ? 'left: 24px;' : 'right: 24px;'}
            width: 380px;
            max-width: calc(100vw - 48px);
            height: 520px;
            max-height: calc(100vh - 140px);
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9998;
        }

        .rag-chat-window.open {
            display: flex;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .rag-chat-header {
            padding: 16px 20px;
            background: ${CONFIG.primaryColor};
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .rag-chat-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
        }

        .rag-chat-close {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .rag-chat-close:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .rag-chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .rag-chat-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .rag-chat-message.user {
            align-self: flex-end;
            background: ${CONFIG.primaryColor};
            color: white;
            border-bottom-right-radius: 4px;
        }

        .rag-chat-message.assistant {
            align-self: flex-start;
            background: #f1f5f9;
            color: #1e293b;
            border-bottom-left-radius: 4px;
        }

        .rag-chat-message.typing {
            display: flex;
            gap: 4px;
            padding: 16px;
        }

        .rag-chat-message.typing span {
            width: 8px;
            height: 8px;
            background: #94a3b8;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .rag-chat-message.typing span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .rag-chat-message.typing span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-8px);
            }
        }

        .rag-chat-input-container {
            padding: 16px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 8px;
        }

        .rag-chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .rag-chat-input:focus {
            border-color: ${CONFIG.primaryColor};
        }

        .rag-chat-send {
            width: 44px;
            height: 44px;
            border: none;
            border-radius: 50%;
            background: ${CONFIG.primaryColor};
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s, transform 0.2s;
        }

        .rag-chat-send:hover:not(:disabled) {
            background: ${CONFIG.primaryColor}dd;
            transform: scale(1.05);
        }

        .rag-chat-send:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }

        .rag-chat-send svg {
            width: 20px;
            height: 20px;
            fill: white;
        }

        .rag-chat-welcome {
            text-align: center;
            color: #64748b;
            padding: 20px;
        }

        .rag-chat-welcome p {
            margin: 8px 0;
            font-size: 14px;
        }

        @media (max-width: 480px) {
            .rag-chat-window {
                width: calc(100vw - 24px);
                height: calc(100vh - 100px);
                bottom: 80px;
                ${CONFIG.position === 'left' ? 'left: 12px;' : 'right: 12px;'}
            }
        }
    `;

    // Chat Widget Class
    class ChatWidget {
        constructor() {
            this.isOpen = false;
            this.conversationId = null;
            this.isLoading = false;
            this.messages = [];

            this.init();
        }

        init() {
            // Inject styles
            const styleSheet = document.createElement('style');
            styleSheet.textContent = STYLES;
            document.head.appendChild(styleSheet);

            // Create widget elements
            this.createBubble();
            this.createWindow();

            // Add welcome message
            this.addMessage('assistant', `Hello! I'm here to help you learn more about this portfolio. Feel free to ask me about skills, projects, experience, or anything else you'd like to know!`);
        }

        createBubble() {
            this.bubble = document.createElement('div');
            this.bubble.className = 'rag-chat-bubble';
            this.bubble.innerHTML = `
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
            `;
            this.bubble.addEventListener('click', () => this.toggle());
            document.body.appendChild(this.bubble);
        }

        createWindow() {
            this.window = document.createElement('div');
            this.window.className = 'rag-chat-window rag-chat-widget';
            this.window.innerHTML = `
                <div class="rag-chat-header">
                    <h3>${CONFIG.title}</h3>
                    <button class="rag-chat-close">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                <div class="rag-chat-messages"></div>
                <div class="rag-chat-input-container">
                    <input type="text" class="rag-chat-input" placeholder="Type your message..." maxlength="2000">
                    <button class="rag-chat-send">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            `;

            // Get elements
            this.messagesContainer = this.window.querySelector('.rag-chat-messages');
            this.input = this.window.querySelector('.rag-chat-input');
            this.sendButton = this.window.querySelector('.rag-chat-send');
            const closeButton = this.window.querySelector('.rag-chat-close');

            // Event listeners
            closeButton.addEventListener('click', () => this.toggle());
            this.sendButton.addEventListener('click', () => this.sendMessage());
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            document.body.appendChild(this.window);
        }

        toggle() {
            this.isOpen = !this.isOpen;
            this.window.classList.toggle('open', this.isOpen);
            if (this.isOpen) {
                this.input.focus();
            }
        }

        addMessage(role, content) {
            const message = document.createElement('div');
            message.className = `rag-chat-message ${role}`;
            message.textContent = content;
            this.messagesContainer.appendChild(message);
            this.scrollToBottom();
            this.messages.push({ role, content });
            return message;
        }

        addTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'rag-chat-message assistant typing';
            indicator.innerHTML = '<span></span><span></span><span></span>';
            this.messagesContainer.appendChild(indicator);
            this.scrollToBottom();
            return indicator;
        }

        scrollToBottom() {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }

        async sendMessage() {
            const message = this.input.value.trim();
            if (!message || this.isLoading) return;

            // Clear input and disable
            this.input.value = '';
            this.isLoading = true;
            this.sendButton.disabled = true;

            // Add user message
            this.addMessage('user', message);

            // Add typing indicator
            const typingIndicator = this.addTypingIndicator();

            try {
                // Send to API with streaming
                const response = await fetch(`${CONFIG.apiUrl}/api/v1/chat/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        conversation_id: this.conversationId,
                    }),
                });

                if (!response.ok) {
                    throw new Error('Failed to get response');
                }

                // Remove typing indicator
                typingIndicator.remove();

                // Create message element for streaming
                const assistantMessage = document.createElement('div');
                assistantMessage.className = 'rag-chat-message assistant';
                this.messagesContainer.appendChild(assistantMessage);

                // Read stream
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullContent = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const text = decoder.decode(value);
                    const lines = text.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                
                                if (data.error) {
                                    assistantMessage.textContent = data.error;
                                } else if (data.content) {
                                    fullContent += data.content;
                                    assistantMessage.textContent = fullContent;
                                    this.scrollToBottom();
                                }

                                if (data.is_final && data.conversation_id) {
                                    this.conversationId = data.conversation_id;
                                }
                            } catch (e) {
                                // Skip invalid JSON
                            }
                        }
                    }
                }

                this.messages.push({ role: 'assistant', content: fullContent });

            } catch (error) {
                console.error('Chat error:', error);
                typingIndicator.remove();
                this.addMessage('assistant', 'I apologize, but I encountered an error. Please try again.');
            } finally {
                this.isLoading = false;
                this.sendButton.disabled = false;
                this.input.focus();
            }
        }
    }

    // Initialize widget when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new ChatWidget());
    } else {
        new ChatWidget();
    }
})();
