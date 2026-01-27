odoo.define('ai_chatbot.FloatingWidget', function (require) {
"use strict";

var Widget = require('web.Widget');
var core = require('web.core');
var ajax = require('web.ajax');
var session = require('web.session');

var _t = core._t;

/**
 * AI Floating Widget - Modern Chat Interface
 * Always accessible from anywhere in Odoo
 */

var FloatingWidget = Widget.extend({
    
    init: function (parent) {
        this._super.apply(this, arguments);
        this.messages = [];
        this.isMinimized = false;
        this.isTyping = false;
        this.slashCommands = this._getSlashCommands();
        this.showSlashMenu = false;
        this.selectedCommandIndex = 0;
    },
    
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._renderWidget();
            self._attachEvents();
            self._loadWelcomeMessage();
            console.log('🚀 AI Floating Widget initialized');
        });
    },
    
    _renderWidget: function () {
        var $body = $('body');
        
        // Float button
        var $floatBtn = $(`
            <div class="o_ai_float_button">
                <span>🤖</span>
            </div>
        `);
        $body.append($floatBtn);
        
        // Main widget
        var $widget = $(`
            <div class="o_ai_floating_widget hidden">
                <!-- Header -->
                <div class="o_ai_widget_header">
                    <div class="o_ai_widget_title">
                        <span class="o_ai_icon">🤖</span>
                        <span>AI Assistant</span>
                    </div>
                    <div class="o_ai_widget_actions">
                        <button class="o_minimize_btn" title="Thu nhỏ">
                            <i class="fa fa-minus"></i>
                        </button>
                        <button class="o_close_btn" title="Đóng">
                            <i class="fa fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="o_ai_quick_actions">
                    <div class="o_ai_quick_action" data-command="summary">
                        📝 Tóm tắt
                    </div>
                    <div class="o_ai_quick_action" data-command="deadline">
                        ⏰ Deadline
                    </div>
                    <div class="o_ai_quick_action" data-command="suggest">
                        💡 Gợi ý
                    </div>
                    <div class="o_ai_quick_action" data-command="create">
                        ➕ Tạo task
                    </div>
                    <div class="o_ai_quick_action" data-command="analytics">
                        📊 Phân tích
                    </div>
                    <div class="o_ai_quick_action" data-command="mytasks">
                        👤 Tasks của tôi
                    </div>
                    <div class="o_ai_quick_action" data-command="report">
                        📈 Báo cáo
                    </div>
                    <div class="o_ai_quick_action" data-command="search">
                        🔍 Tìm kiếm
                    </div>
                </div>
                
                <!-- Messages -->
                <div class="o_ai_widget_messages">
                    <div class="o_ai_empty_state">
                        <div class="o_icon">🤖</div>
                        <div class="o_title">AI Assistant Pro</div>
                        <div class="o_description">
                            28+ Commands | Smart Search | Analytics<br>
                            <strong>Gõ / để bắt đầu</strong>
                        </div>
                    </div>
                </div>
                
                <!-- Input -->
                <div class="o_ai_widget_input">
                    <div class="o_ai_slash_menu" style="display: none;"></div>
                    <div class="o_ai_input_wrapper">
                        <div class="o_ai_input_field">
                            <textarea placeholder="Gõ / để xem commands..." rows="1"></textarea>
                            <span class="o_ai_slash_hint">/ commands</span>
                        </div>
                        <button class="o_ai_send_btn">
                            <i class="fa fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `);
        $body.append($widget);
        
        this.$floatBtn = $floatBtn;
        this.$widget = $widget;
        this.$messages = $widget.find('.o_ai_widget_messages');
        this.$input = $widget.find('textarea');
        this.$slashMenu = $widget.find('.o_ai_slash_menu');
    },
    
    _attachEvents: function () {
        var self = this;
        
        // Float button click
        this.$floatBtn.on('click', function () {
            self._showWidget();
        });
        
        // Close button
        this.$widget.find('.o_close_btn').on('click', function (e) {
            e.stopPropagation();
            self._hideWidget();
        });
        
        // Minimize button
        this.$widget.find('.o_minimize_btn').on('click', function (e) {
            e.stopPropagation();
            self._toggleMinimize();
        });
        
        // Click header khi minimized để maximize
        this.$widget.find('.o_ai_widget_header').on('click', function (e) {
            if (self.isMinimized && !$(e.target).closest('button').length) {
                self._toggleMinimize();
            }
        });
        
        // Send button
        this.$widget.find('.o_ai_send_btn').on('click', function () {
            self._sendMessage();
        });
        
        // Input events
        this.$input.on('keydown', function (ev) {
            self._handleInputKeydown(ev);
        });
        
        this.$input.on('input', function () {
            self._handleInputChange();
            self._autoResize();
        });
        
        // Quick actions
        this.$widget.find('.o_ai_quick_action').on('click', function () {
            var command = $(this).data('command');
            self._executeQuickAction(command);
        });
        
        // Make header draggable
        this._makeDraggable();
    },
    
    _handleInputKeydown: function (ev) {
        // Enter without Shift = send
        if (ev.key === 'Enter' && !ev.shiftKey) {
            ev.preventDefault();
            this._sendMessage();
            return;
        }
        
        // Navigate slash menu
        if (this.showSlashMenu) {
            if (ev.key === 'ArrowDown') {
                ev.preventDefault();
                this._navigateSlashMenu(1);
            } else if (ev.key === 'ArrowUp') {
                ev.preventDefault();
                this._navigateSlashMenu(-1);
            } else if (ev.key === 'Enter') {
                ev.preventDefault();
                this._selectSlashCommand();
            } else if (ev.key === 'Escape') {
                this._hideSlashMenu();
            }
        }
    },
    
    _handleInputChange: function () {
        var value = this.$input.val();
        
        // Show slash menu if starts with /
        if (value.startsWith('/')) {
            var query = value.substring(1).toLowerCase();
            this._showSlashMenu(query);
        } else {
            this._hideSlashMenu();
        }
    },
    
    _autoResize: function () {
        this.$input.css('height', 'auto');
        this.$input.css('height', this.$input[0].scrollHeight + 'px');
    },
    
    _sendMessage: function () {
        var self = this;
        var message = this.$input.val().trim();
        
        if (!message) return;
        
        // Add user message
        this._addMessage('user', message);
        this.$input.val('').css('height', 'auto');
        
        // Show typing indicator
        this._showTyping();
        
        // Process message
        this._processMessage(message).then(function (response) {
            self._hideTyping();
            self._addMessage('ai', response);
        }).catch(function (error) {
            self._hideTyping();
            self._addMessage('ai', '❌ Xin lỗi, có lỗi xảy ra: ' + (error.message || 'Unknown error'));
        });
    },
    
    _processMessage: function (message) {
        var self = this;
        
        // Simulated processing - replace with actual AI endpoint
        return ajax.jsonRpc('/ai_chatbot/process_message', 'call', {
            room_id: 1, // Default room or current context
            message: message
        }).then(function (result) {
            if (result.success) {
                return result.message;
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        });
    },
    
    _addMessage: function (type, content) {
        // Remove empty state
        this.$messages.find('.o_ai_empty_state').remove();
        
        var time = new Date().toLocaleTimeString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        var $message = $(`
            <div class="o_ai_message_bubble ${type}">
                <div class="o_ai_message_content">
                    ${this._formatMessage(content)}
                </div>
                <div class="o_ai_message_time">${time}</div>
            </div>
        `);
        
        this.$messages.append($message);
        this._scrollToBottom();
        
        this.messages.push({type: type, content: content, time: time});
    },
    
    _formatMessage: function (content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    },
    
    _showTyping: function () {
        if (this.isTyping) return;
        this.isTyping = true;
        
        var $typing = $(`
            <div class="o_ai_message_bubble ai typing">
                <div class="o_ai_typing">
                    <div class="o_ai_typing_dot"></div>
                    <div class="o_ai_typing_dot"></div>
                    <div class="o_ai_typing_dot"></div>
                </div>
            </div>
        `);
        
        this.$messages.append($typing);
        this._scrollToBottom();
    },
    
    _hideTyping: function () {
        this.isTyping = false;
        this.$messages.find('.typing').remove();
    },
    
    _scrollToBottom: function () {
        this.$messages.scrollTop(this.$messages[0].scrollHeight);
    },
    
    _showWidget: function () {
        this.$widget.removeClass('hidden');
        this.$floatBtn.addClass('hidden');
        this.$input.focus();
    },
    
    _hideWidget: function () {
        this.$widget.addClass('hidden');
        this.$floatBtn.removeClass('hidden');
        
        // Reset position về mặc định
        this.$widget.css({
            left: 'auto',
            top: 'auto',
            right: '20px',
            bottom: '80px'
        });
    },
    
    _toggleMinimize: function () {
        var self = this;
        this.isMinimized = !this.isMinimized;
        
        var $minBtn = this.$widget.find('.o_minimize_btn');
        
        if (this.isMinimized) {
            // Thu nhỏ - reset position
            this.$widget.css({
                left: 'auto',
                top: 'auto',
                right: '20px',
                bottom: '80px'
            });
            this.$widget.addClass('minimized');
            $minBtn.find('i').removeClass('fa-minus').addClass('fa-window-maximize');
            $minBtn.attr('title', 'Phóng to');
        } else {
            // Phóng to - khôi phục vị trí đã lưu
            this._restoreSavedPosition();
            this.$widget.removeClass('minimized');
            $minBtn.find('i').removeClass('fa-window-maximize').addClass('fa-minus');
            $minBtn.attr('title', 'Thu nhỏ');
            // Focus vào input sau khi phóng to
            setTimeout(function() {
                self.$input.focus();
            }, 300);
        }
    },
    
    _showSlashMenu: function (query) {
        var self = this;
        this.showSlashMenu = true;
        this.selectedCommandIndex = 0;
        
        // Filter commands
        var filtered = this.slashCommands.filter(function (cmd) {
            return cmd.command.includes(query) || cmd.title.toLowerCase().includes(query);
        });
        
        // Render menu
        this.$slashMenu.empty();
        filtered.forEach(function (cmd, index) {
            var $item = $(`
                <div class="o_ai_slash_menu_item ${index === 0 ? 'selected' : ''}" data-index="${index}">
                    <div class="o_icon">${cmd.icon}</div>
                    <div class="o_info">
                        <div class="o_title">/${cmd.command}</div>
                        <div class="o_description">${cmd.description}</div>
                    </div>
                    <div class="o_shortcut">${cmd.shortcut || ''}</div>
                </div>
            `);
            
            $item.on('click', function () {
                self._executeSlashCommand(cmd);
            });
            
            self.$slashMenu.append($item);
        });
        
        this.$slashMenu.show();
        this.filteredCommands = filtered;
    },
    
    _hideSlashMenu: function () {
        this.showSlashMenu = false;
        this.$slashMenu.hide();
    },
    
    _navigateSlashMenu: function (direction) {
        this.selectedCommandIndex += direction;
        var max = this.filteredCommands.length - 1;
        
        if (this.selectedCommandIndex < 0) this.selectedCommandIndex = max;
        if (this.selectedCommandIndex > max) this.selectedCommandIndex = 0;
        
        // Update UI
        this.$slashMenu.find('.o_ai_slash_menu_item').removeClass('selected');
        this.$slashMenu.find(`.o_ai_slash_menu_item[data-index="${this.selectedCommandIndex}"]`).addClass('selected');
    },
    
    _selectSlashCommand: function () {
        var cmd = this.filteredCommands[this.selectedCommandIndex];
        if (cmd) {
            this._executeSlashCommand(cmd);
        }
    },
    
    _executeSlashCommand: function (cmd) {
        this._hideSlashMenu();
        this.$input.val('').css('height', 'auto');
        
        // Execute command
        this._addMessage('user', '/' + cmd.command);
        this._showTyping();
        
        var self = this;
        this._processSlashCommand(cmd).then(function (response) {
            self._hideTyping();
            self._addMessage('ai', response);
        });
    },
    
    _processSlashCommand: function (cmd) {
        // Map slash commands to AI intents
        var intentMap = {
            // Tóm tắt & Phân tích
            'summary': '@ai tóm tắt chat hôm nay',
            'recap': '@ai tóm tắt tuần này',
            'analytics': '@ai phân tích hiệu suất làm việc',
            'report': '@ai báo cáo chi tiết dự án',
            
            // Quản lý Tasks
            'tasks': '@ai có bao nhiêu task?',
            'mytasks': '@ai tasks của tôi là gì?',
            'create': '@ai tạo task mới',
            'assign': '@ai gán task cho người khác',
            'update': '@ai cập nhật trạng thái task',
            
            // Deadline & Cảnh báo
            'deadline': '@ai task nào sắp deadline?',
            'warning': '@ai task nào trễ hạn?',
            'today': '@ai việc cần làm hôm nay',
            'tomorrow': '@ai việc cần làm ngày mai',
            
            // Tìm kiếm & Lọc
            'search': '@ai tìm kiếm task',
            'filter': '@ai lọc tasks theo điều kiện',
            'priority': '@ai tasks ưu tiên cao',
            
            // Gợi ý & Coaching
            'suggest': '@ai nên làm gì tiếp theo?',
            'tips': '@ai cho tôi mẹo làm việc hiệu quả',
            'motivation': '@ai động viên tôi',
            
            // Thống kê & Export
            'stats': '@ai thống kê tổng quan',
            'progress': '@ai tiến độ của tôi',
            'export': '@ai xuất dữ liệu tasks',
            
            // Team & Collaboration
            'team': '@ai thông tin team',
            'members': '@ai danh sách thành viên',
            'meeting': '@ai tạo meeting notes',
            
            // Trợ giúp
            'help': '@ai giúp tôi với',
            'shortcuts': '@ai danh sách phím tắt'
        };
        
        var message = intentMap[cmd.command] || '@ai ' + cmd.description;
        return this._processMessage(message);
    },
    
    _executeQuickAction: function (action) {
        var commands = {
            'summary': {command: 'summary'},
            'deadline': {command: 'deadline'},
            'suggest': {command: 'suggest'},
            'create': {command: 'create'},
            'analytics': {command: 'analytics'},
            'mytasks': {command: 'mytasks'},
            'report': {command: 'report'},
            'search': {command: 'search'}
        };
        
        var cmd = commands[action];
        if (cmd) {
            this._executeSlashCommand(cmd);
        }
    },
    
    _getSlashCommands: function () {
        return [
            // Tóm tắt & Phân tích
            {command: 'summary', icon: '📝', title: 'Tóm tắt', description: 'Tóm tắt chat hôm nay', shortcut: '⌘S'},
            {command: 'recap', icon: '📊', title: 'Recap', description: 'Tóm tắt tuần này'},
            {command: 'analytics', icon: '📈', title: 'Analytics', description: 'Phân tích hiệu suất làm việc'},
            {command: 'report', icon: '📋', title: 'Report', description: 'Báo cáo chi tiết dự án'},
            
            // Quản lý Tasks
            {command: 'tasks', icon: '✅', title: 'Tasks', description: 'Danh sách tất cả tasks', shortcut: '⌘T'},
            {command: 'mytasks', icon: '👤', title: 'My Tasks', description: 'Tasks được giao cho tôi'},
            {command: 'create', icon: '➕', title: 'Create', description: 'Tạo task mới'},
            {command: 'assign', icon: '👥', title: 'Assign', description: 'Gán task cho người khác'},
            {command: 'update', icon: '🔄', title: 'Update', description: 'Cập nhật trạng thái task'},
            
            // Deadline & Cảnh báo
            {command: 'deadline', icon: '⏰', title: 'Deadline', description: 'Tasks sắp đến hạn'},
            {command: 'warning', icon: '⚠️', title: 'Warning', description: 'Tasks trễ hạn'},
            {command: 'today', icon: '📅', title: 'Today', description: 'Việc cần làm hôm nay'},
            {command: 'tomorrow', icon: '🔜', title: 'Tomorrow', description: 'Việc cần làm ngày mai'},
            
            // Tìm kiếm & Lọc
            {command: 'search', icon: '🔍', title: 'Search', description: 'Tìm kiếm tasks theo từ khóa'},
            {command: 'filter', icon: '🎯', title: 'Filter', description: 'Lọc tasks theo điều kiện'},
            {command: 'priority', icon: '🔴', title: 'Priority', description: 'Tasks ưu tiên cao'},
            
            // Gợi ý & Coaching
            {command: 'suggest', icon: '💡', title: 'Suggest', description: 'Gợi ý task tiếp theo'},
            {command: 'tips', icon: '✨', title: 'Tips', description: 'Mẹo làm việc hiệu quả'},
            {command: 'motivation', icon: '🚀', title: 'Motivation', description: 'Động lực làm việc'},
            
            // Thống kê & Export
            {command: 'stats', icon: '📊', title: 'Stats', description: 'Thống kê tổng quan'},
            {command: 'progress', icon: '📈', title: 'Progress', description: 'Theo dõi tiến độ cá nhân'},
            {command: 'export', icon: '💾', title: 'Export', description: 'Xuất dữ liệu tasks'},
            
            // Team & Collaboration
            {command: 'team', icon: '👥', title: 'Team', description: 'Thông tin team'},
            {command: 'members', icon: '👨‍💼', title: 'Members', description: 'Danh sách thành viên'},
            {command: 'meeting', icon: '🤝', title: 'Meeting', description: 'Tạo meeting notes'},
            
            // Trợ giúp
            {command: 'help', icon: '❓', title: 'Help', description: 'Hướng dẫn sử dụng'},
            {command: 'shortcuts', icon: '⌨️', title: 'Shortcuts', description: 'Danh sách phím tắt'}
        ];
    },
    
    _loadWelcomeMessage: function () {
        var self = this;
        setTimeout(function () {
            var welcome = '👋 **Xin chào! Tôi là AI Assistant.**\n\n' +
                '**Tôi có thể giúp bạn:**\n' +
                '• 📝 Tóm tắt & phân tích hiệu suất\n' +
                '• ✅ Quản lý tasks & deadline\n' +
                '• 🔍 Tìm kiếm & lọc tasks\n' +
                '• 💡 Gợi ý & động viên\n' +
                '• 📊 Thống kê & báo cáo\n\n' +
                '**Cách sử dụng:**\n' +
                '• Gõ **/** để xem 28+ commands\n' +
                '• Click các nút Quick Actions\n' +
                '• Hoặc hỏi bằng ngôn ngữ tự nhiên\n\n' +
                '_Thử ngay: /help hoặc /tasks_';
            
            // Add welcome message after a short delay
            // self._addMessage('ai', welcome);
        }, 1000);
    },
    
    _makeDraggable: function () {
        var self = this;
        var $header = this.$widget.find('.o_ai_widget_header');
        var isDragging = false;
        var currentX, currentY, initialX, initialY;
        
        $header.on('mousedown', function (e) {
            if ($(e.target).closest('button').length) return;
            
            isDragging = true;
            initialX = e.clientX - self.$widget.offset().left;
            initialY = e.clientY - self.$widget.offset().top;
            
            $header.css('cursor', 'grabbing');
            self.$widget.css({
                transition: 'none',
                opacity: 0.9
            });
        });
        
        $(document).on('mousemove', function (e) {
            if (!isDragging) return;
            
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            
            // Giới hạn trong viewport
            var maxX = window.innerWidth - self.$widget.outerWidth();
            var maxY = window.innerHeight - self.$widget.outerHeight();
            
            currentX = Math.max(0, Math.min(currentX, maxX));
            currentY = Math.max(0, Math.min(currentY, maxY));
            
            self.$widget.css({
                left: currentX + 'px',
                top: currentY + 'px',
                right: 'auto',
                bottom: 'auto'
            });
        });
        
        $(document).on('mouseup', function () {
            if (isDragging) {
                isDragging = false;
                $header.css('cursor', 'move');
                self.$widget.css({
                    transition: '',
                    opacity: 1
                });
                
                // Save position to localStorage
                localStorage.setItem('ai_widget_position', JSON.stringify({
                    left: self.$widget.css('left'),
                    top: self.$widget.css('top')
                }));
            }
        });
        
        // Restore saved position
        this._restorePosition();
    },
    
    _restorePosition: function () {
        var saved = localStorage.getItem('ai_widget_position');
        if (saved) {
            try {
                var pos = JSON.parse(saved);
                this.$widget.css({
                    left: pos.left,
                    top: pos.top,
                    right: 'auto',
                    bottom: 'auto'
                });
            } catch (e) {
                console.warn('Failed to restore widget position');
            }
        }
    },
    
    _restoreSavedPosition: function () {
        var saved = localStorage.getItem('ai_widget_position');
        if (saved) {
            try {
                var pos = JSON.parse(saved);
                this.$widget.css({
                    left: pos.left,
                    top: pos.top,
                    right: 'auto',
                    bottom: 'auto'
                });
            } catch (e) {
                // Nếu không có lưu, giữ nguyên vị trí mặc định
            }
        }
    },
    
});

// Auto-initialize on page load
core.bus.on('web_client_ready', null, function () {
    var widget = new FloatingWidget();
    widget.appendTo($('body'));
    console.log('✅ AI Floating Widget loaded');
});

return FloatingWidget;

});
