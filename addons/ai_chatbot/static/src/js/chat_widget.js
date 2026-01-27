odoo.define('ai_chatbot.ChatWidget', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var FormController = require('web.FormController');
var _t = core._t;

/**
 * AI Chatbot Widget cho Odoo 15 - Tích hợp vào Chat Nội Bộ
 * Tự động kích hoạt khi mở chat.room form view
 */

var AIChatbotWidget = {
    
    init: function(roomId) {
        this.roomId = roomId;
        this.messages = [];
        this.setupEventListeners();
        this.loadMessages();
        
        // Auto refresh every 10 seconds
        this.refreshInterval = setInterval(() => {
            this.loadMessages();
        }, 10000);
    },
    
    setupEventListeners: function() {
        var self = this;
        
        $(document).on('click', '#ai_send_btn', function() {
            self.sendMessage();
        });
        
        $(document).on('click', '#ai_ask_btn', function() {
            self.insertAiPrefix();
        });
        
        $(document).on('keypress', '#ai_chat_input', function(e) {
            if (e.which === 13) {
                self.sendMessage();
            }
        });
    },
    
    loadMessages: function() {
        var self = this;
        var $container = $('#ai_chat_messages');
        
        if (!this.roomId || $container.length === 0) {
            return;
        }
        
        ajax.jsonRpc('/ai_chatbot/get_messages', 'call', {
            room_id: this.roomId,
            limit: 50
        }).then(function(result) {
            if (result.success) {
                self.messages = result.messages;
                self.renderMessages();
            }
        }).catch(function(error) {
            console.error('Error loading messages:', error);
        });
    },
    
    sendMessage: function() {
        var self = this;
        var $input = $('#ai_chat_input');
        var $sendBtn = $('#ai_send_btn');
        var message = $input.val().trim();
        
        if (!message || !this.roomId) {
            return;
        }
        
        // Disable input
        $input.prop('disabled', true);
        $sendBtn.prop('disabled', true);
        
        var isAiMessage = message.toLowerCase().startsWith('@ai');
        
        if (isAiMessage) {
            this.showTypingIndicator();
        }
        
        ajax.jsonRpc('/ai_chatbot/send_message', 'call', {
            room_id: this.roomId,
            message: message
        }).then(function(result) {
            if (result.success) {
                $input.val('');
                self.loadMessages();
            } else {
                alert('Lỗi: ' + (result.error || 'Unknown error'));
            }
        }).catch(function(error) {
            console.error('Error sending message:', error);
            alert('Lỗi khi gửi tin nhắn');
        }).finally(function() {
            self.hideTypingIndicator();
            $input.prop('disabled', false);
            $sendBtn.prop('disabled', false);
            $input.focus();
        });
    },
    
    insertAiPrefix: function() {
        var $input = $('#ai_chat_input');
        $input.val('@ai ');
        $input.focus();
    },
    
    renderMessages: function() {
        var $container = $('#ai_chat_messages');
        
        if ($container.length === 0) {
            return;
        }
        
        $container.empty();
        
        this.messages.forEach(function(msg) {
            var $messageDiv = $('<div>')
                .addClass('o_ai_message')
                .addClass(msg.is_ai_response ? 'o_ai_response' : 'o_user_message');
            
            var avatar = msg.is_ai_response ? '🤖' : '👤';
            var content = msg.content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
            
            var timestamp = msg.create_date ? new Date(msg.create_date).toLocaleTimeString('vi-VN', {
                hour: '2-digit',
                minute: '2-digit'
            }) : '';
            
            $messageDiv.html(
                '<div class="o_message_header">' +
                    '<span class="o_avatar">' + avatar + '</span>' +
                    '<span class="o_sender">' + msg.sender_name + '</span>' +
                    '<span class="o_time">' + timestamp + '</span>' +
                '</div>' +
                '<div class="o_message_body">' + content + '</div>'
            );
            
            $container.append($messageDiv);
        });
        
        // Scroll to bottom
        $container.scrollTop($container[0].scrollHeight);
    },
    
    showTypingIndicator: function() {
        var $container = $('#ai_chat_messages');
        
        if ($container.length === 0) {
            return;
        }
        
        var $indicator = $('<div>')
            .attr('id', 'ai_typing_indicator')
            .addClass('o_typing_indicator')
            .html(
                '🤖 AI Assistant đang suy nghĩ' +
                '<span class="o_dot"></span>' +
                '<span class="o_dot"></span>' +
                '<span class="o_dot"></span>'
            );
        
        $container.append($indicator);
        $container.scrollTop($container[0].scrollHeight);
    },
    
    hideTypingIndicator: function() {
        $('#ai_typing_indicator').remove();
    },
    
    destroy: function() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        $(document).off('click', '#ai_send_btn');
        $(document).off('click', '#ai_ask_btn');
        $(document).off('keypress', '#ai_chat_input');
    }
};

// Extend FormController để tự động init AI chat widget
FormController.include({
    
    _update: function() {
        var result = this._super.apply(this, arguments);
        
        // Init AI chat widget when chat.room form is loaded
        if (this.modelName === 'chat.room') {
            this._initAIChatWidget();
        }
        
        return result;
    },
    
    _initAIChatWidget: function() {
        var self = this;
        
        // Đợi DOM render xong
        setTimeout(function() {
            var roomId = self.model.get(self.handle).res_id;
            
            if (roomId && $('#ai_chat_messages').length > 0) {
                // Destroy old widget nếu có
                if (self.aiChatWidget) {
                    self.aiChatWidget.destroy();
                }
                
                // Init new widget
                self.aiChatWidget = Object.create(AIChatbotWidget);
                self.aiChatWidget.init(roomId);
            }
        }, 300);
    },
    
    destroy: function() {
        if (this.aiChatWidget) {
            this.aiChatWidget.destroy();
        }
        this._super.apply(this, arguments);
    }
});

return AIChatbotWidget;

});
