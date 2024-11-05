(function($) {
    'use strict';

    class RAGChatbot {
        constructor() {
            this.container = $('#rag-chatbot-container');
            this.messagesContainer = $('#rag-chatbot-messages');
            this.input = $('#rag-chatbot-input');
            this.sendButton = $('#rag-chatbot-send');
            this.toggleButton = $('#rag-chatbot-toggle');
            this.context = [];
            this.isOpen = false;

            this.initializeEventListeners();
        }

        initializeEventListeners() {
            this.sendButton.on('click', () => this.handleSend());
            this.input.on('keypress', (e) => {
                if (e.which === 13 && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSend();
                }
            });
            this.toggleButton.on('click', () => this.toggleChat());
        }

        toggleChat() {
            this.isOpen = !this.isOpen;
            this.container.toggleClass('rag-chatbot-open');
            if (this.isOpen) {
                this.input.focus();
            }
        }

        async handleSend() {
            const message = this.input.val().trim();
            if (!message) return;

            this.input.val('');
            this.addMessage(message, 'user');

            this.showTypingIndicator();

            try {
                const response = await this.sendQuery(message);
                this.hideTypingIndicator();
                
                if (response.success && response.data) {
                    // Add the response to the chat
                    this.addMessage(response.data.response, 'bot');
                    
                    // Display thought process if available
                    if (response.data.thought_process && response.data.thought_process.length > 0) {
                        this.addThoughtProcess(response.data.thought_process);
                    }
                    
                    // Update context
                    this.context.push(message);
                    this.context.push(response.data.response);
                    if (this.context.length > 6) {
                        this.context = this.context.slice(-6);
                    }
                } else {
                    this.addMessage('Sorry, I encountered an error processing your request.', 'bot');
                }
            } catch (error) {
                this.hideTypingIndicator();
                this.addMessage('Sorry, I encountered an error processing your request.', 'bot');
                console.error('Error:', error);
            }
        }

        async sendQuery(message) {
            return $.ajax({
                url: ragChatbot.ajax_url,
                method: 'POST',
                data: {
                    action: 'rag_chatbot_query',
                    nonce: ragChatbot.nonce,
                    query: message,
                    context: this.context
                }
            });
        }

        addMessage(message, type) {
            const messageElement = $('<div>')
                .addClass(`rag-chatbot-message ${type}-message`)
                .text(message);
            
            this.messagesContainer.append(messageElement);
            this.scrollToBottom();
        }

        addThoughtProcess(thoughts) {
            const thoughtsContainer = $('<div>')
                .addClass('rag-chatbot-thoughts');
            
            thoughts.forEach(thought => {
                $('<div>')
                    .addClass('rag-chatbot-thought')
                    .text(thought)
                    .appendTo(thoughtsContainer);
            });
            
            this.messagesContainer.append(thoughtsContainer);
            this.scrollToBottom();
        }

        showTypingIndicator() {
            const typingIndicator = $('<div>')
                .addClass('rag-chatbot-typing')
                .text('Thinking...');
            this.messagesContainer.append(typingIndicator);
            this.scrollToBottom();
        }

        hideTypingIndicator() {
            this.messagesContainer.find('.rag-chatbot-typing').remove();
        }

        scrollToBottom() {
            this.messagesContainer.scrollTop(this.messagesContainer[0].scrollHeight);
        }
    }

    // Initialize chatbot when document is ready
    $(document).ready(() => {
        new RAGChatbot();
    });

})(jQuery);