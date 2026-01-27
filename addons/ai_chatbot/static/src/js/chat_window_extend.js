odoo.define('ai_chatbot.ChatWindowExtend', function (require) {
"use strict";

var ChatWindow = require('chat_noi_bo.ChatWindow');
var ajax = require('web.ajax');

/**
 * Extend Chat Window để tích hợp AI Assistant
 * Intercept tin nhắn bắt đầu bằng @ai và xử lý qua AI endpoint
 */

ChatWindow.include({
    
    _sendMessage: function () {
        var self = this;
        var $textarea = this.$('.o_chat_input textarea');
        var content = $textarea.val().trim();
        
        if (!content) {
            return;
        }
        
        if (!this.selectedRoom || !this.currentEmployee) {
            return this._super.apply(this, arguments);
        }
        
        // Kiểm tra xem tin nhắn có bắt đầu bằng @ai không
        var isAiMessage = content.toLowerCase().startsWith('@ai');
        
        if (isAiMessage) {
            console.log('🤖 AI message detected:', content);
            
            // Hiển thị typing indicator
            this._showAiTypingIndicator();
            
            // Gửi tin nhắn qua AI endpoint
            return ajax.jsonRpc('/ai_chatbot/send_message', 'call', {
                room_id: this.selectedRoom.id,
                message: content
            }).then(function (result) {
                console.log('🤖 AI response:', result);
                
                // Clear input
                $textarea.val('');
                
                // Ẩn typing indicator
                self._hideAiTypingIndicator();
                
                if (result.success) {
                    // Reload messages để hiện cả tin nhắn user và AI response
                    return self._loadMessages();
                } else {
                    // Hiển thị lỗi
                    self.displayNotification({
                        title: 'AI Error',
                        message: result.error || 'Không thể xử lý yêu cầu AI',
                        type: 'danger',
                    });
                }
            }).catch(function (error) {
                console.error('❌ AI error:', error);
                self._hideAiTypingIndicator();
                self.displayNotification({
                    title: 'Lỗi AI',
                    message: 'Không thể kết nối với AI Assistant',
                    type: 'danger',
                });
            });
        } else {
            // Tin nhắn thường - gọi hàm cha
            return this._super.apply(this, arguments);
        }
    },
    
    _showAiTypingIndicator: function () {
        var $messages = this.$('.o_chat_messages');
        if ($messages.length === 0) return;
        
        // Xóa indicator cũ nếu có
        this._hideAiTypingIndicator();
        
        var $indicator = $(`
            <div class="o_ai_typing_indicator" style="
                padding: 15px;
                margin: 10px 0;
                background: #f0f0f0;
                border-radius: 10px;
                text-align: center;
                animation: pulse 1.5s ease-in-out infinite;
            ">
                <span style="font-size: 24px;">🤖</span>
                <span style="margin-left: 10px; color: #667eea; font-weight: 600;">
                    AI Assistant đang suy nghĩ...
                </span>
                <span class="o_dot" style="display: inline-block; width: 8px; height: 8px; 
                    background: #667eea; border-radius: 50%; margin: 0 2px; 
                    animation: typing 1.4s infinite;">
                </span>
                <span class="o_dot" style="display: inline-block; width: 8px; height: 8px; 
                    background: #667eea; border-radius: 50%; margin: 0 2px; 
                    animation: typing 1.4s infinite 0.2s;">
                </span>
                <span class="o_dot" style="display: inline-block; width: 8px; height: 8px; 
                    background: #667eea; border-radius: 50%; margin: 0 2px; 
                    animation: typing 1.4s infinite 0.4s;">
                </span>
            </div>
        `);
        
        $messages.append($indicator);
        $messages.scrollTop($messages[0].scrollHeight);
    },
    
    _hideAiTypingIndicator: function () {
        this.$('.o_ai_typing_indicator').remove();
    },
    
});

// Add CSS animations for typing indicator
if (typeof document !== 'undefined') {
    var style = document.createElement('style');
    style.textContent = `
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
            30% { transform: translateY(-10px); opacity: 1; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
    `;
    document.head.appendChild(style);
}

console.log('✅ AI Chatbot integrated into Chat Window');

return ChatWindow;

});
