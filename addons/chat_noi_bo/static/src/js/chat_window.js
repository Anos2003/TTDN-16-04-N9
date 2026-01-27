odoo.define('chat_noi_bo.ChatWindow', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var session = require('web.session');

var ChatWindow = AbstractAction.extend({
    hasControlPanel: false,
    
    events: {
        'click .o_chat_room_item': '_onRoomClick',
        'click .btn-primary[data-action="send"]': '_onSendMessage',
        'keypress .o_chat_input textarea': '_onKeyPress',
        'click button[data-action="refresh"]': '_onRefresh',
    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.rooms = [];
        this.selectedRoom = null;
        this.messages = [];
        this.currentEmployee = null;
        this.refreshInterval = null;
        this.roomRefreshInterval = null;
        this._isCheckingMessages = false;
        this._scrollTimeout = null;
    },

    willStart: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return self._loadCurrentEmployee();
        });
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            // Render initial HTML
            self._renderMainTemplate();
            // Load rooms after DOM is ready
            return self._loadRooms();
        }).then(function () {
            console.log('✅ Chat started - Realtime polling (3s)');
            
            // Polling tối ưu: 3 giây cho realtime, nhưng chỉ check khi có room
            self.refreshInterval = setInterval(function () {
                if (self.selectedRoom && !self._isCheckingMessages) {
                    self._checkNewMessages();
                }
            }, 3000);
            
            // Refresh room list mỗi 10 giây để cập nhật thời gian
            self.roomRefreshInterval = setInterval(function () {
                self._refreshRoomList();
            }, 10000);
        });
    },
    
    _renderMainTemplate: function () {
        this.$el.html(`
            <div class="o_chat_window">
                <div class="o_chat_sidebar">
                    <div class="o_chat_sidebar_header">
                        <h3>💬 Chat</h3>
                        <button class="btn btn-sm btn-primary" data-action="refresh">
                            <i class="fa fa-refresh"/>
                        </button>
                    </div>
                    <div class="o_chat_room_list"></div>
                </div>
                <div class="o_chat_main">
                    <div class="o_chat_empty">
                        <i class="fa fa-comments-o fa-4x"/>
                        <p>Chọn một phòng chat để bắt đầu</p>
                    </div>
                </div>
            </div>
        `);
    },

    destroy: function () {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        if (this.roomRefreshInterval) {
            clearInterval(this.roomRefreshInterval);
        }
        this._super.apply(this, arguments);
    },

    _loadCurrentEmployee: function () {
        var self = this;
        return this._rpc({
            model: 'nhan_vien',
            method: 'search_read',
            domain: [['user_id', '=', this.getSession().uid]],
            fields: ['id', 'ten'],
        }).then(function (result) {
            if (result.length > 0) {
                self.currentEmployee = result[0];
                console.log('Nhân viên hiện tại:', self.currentEmployee);
            } else {
                console.warn('Không tìm thấy nhân viên cho user ID:', self.getSession().uid);
                console.warn('User name:', self.getSession().name);
                // Hiển thị cảnh báo cho user
                self.displayNotification({
                    title: 'Cảnh báo',
                    message: 'Bạn chưa có thông tin nhân viên. Một số tính năng chat có thể bị giới hạn.',
                    type: 'warning',
                    sticky: true,
                });
            }
        });
    },

    _loadRooms: function () {
        var self = this;
        return this._rpc({
            model: 'chat.room',
            method: 'get_accessible_rooms',
            args: [],
        }).then(function (rooms) {
            self.rooms = rooms;
            self._renderRooms();
        });
    },
    
    _loadRoomDetails: function (roomId) {
        var self = this;
        return this._rpc({
            model: 'chat.room',
            method: 'read',
            args: [[roomId], ['id', 'name', 'is_announcement_room']],
        }).then(function (result) {
            if (result && result.length > 0) {
                return result[0];
            }
            return {};
        });
    },

    _loadMessages: function () {
        var self = this;
        if (!this.selectedRoom) return Promise.resolve();
        
        return this._rpc({
            model: 'chat.message',
            method: 'search_read',
            domain: [['room_id', '=', this.selectedRoom.id]],
            fields: ['id', 'content', 'sender_id', 'create_date', 'message_type', 'is_read_by_me'],
            orderBy: [{name: 'create_date', asc: true}],
        }).then(function (messages) {
            self.messages = messages;
            self._renderMessages();
            
            // Mark messages as read
            var unreadIds = messages.filter(function (m) { return !m.is_read_by_me; })
                                    .map(function (m) { return m.id; });
            if (unreadIds.length > 0) {
                return self._rpc({
                    model: 'chat.message',
                    method: 'action_mark_as_read',
                    args: [unreadIds],
                });
            }
        }).then(function () {
            self._scrollToBottom();
        });
    },
    
    _checkNewMessages: function () {
        var self = this;
        if (!this.selectedRoom || !this.messages || this._isCheckingMessages) {
            return Promise.resolve();
        }
        
        this._isCheckingMessages = true;
        
        // Lấy ID tin nhắn cuối cùng
        var lastMessageId = this.messages.length > 0 ? this.messages[this.messages.length - 1].id : 0;
        
        return this._rpc({
            model: 'chat.message',
            method: 'search_read',
            domain: [
                ['room_id', '=', this.selectedRoom.id],
                ['id', '>', lastMessageId]
            ],
            fields: ['id', 'content', 'sender_id', 'create_date', 'message_type', 'is_read_by_me'],
            orderBy: [{name: 'create_date', asc: true}],
        }).then(function (newMessages) {
            self._isCheckingMessages = false;
            
            if (newMessages && newMessages.length > 0) {
                console.log('✨ Found', newMessages.length, 'new messages');
                // Thêm tin nhắn mới vào array
                self.messages = self.messages.concat(newMessages);
                
                // Chễ append tin nhắn mới vào DOM thay vì render lại toàn bộ
                self._appendMessages(newMessages, true);
                
                // Mark as read
                var unreadIds = newMessages.filter(function (m) { return !m.is_read_by_me; })
                                          .map(function (m) { return m.id; });
                if (unreadIds.length > 0) {
                    self._rpc({
                        model: 'chat.message',
                        method: 'action_mark_as_read',
                        args: [unreadIds],
                    });
                }
                
                // Refresh room list để cập nhật thời gian
                self._refreshRoomList();
                
                // Smooth scroll xuống với debounce
                self._debouncedScrollToBottom();
            } else {
                self._isCheckingMessages = false;
            }
        }).catch(function(error) {
            self._isCheckingMessages = false;
            console.error('Error checking new messages:', error);
        });
    },

    _renderRooms: function () {
        var self = this;
        var $roomList = this.$('.o_chat_room_list');
        if (!$roomList || $roomList.length === 0) {
            console.warn('Room list container not found');
            return;
        }
        
        $roomList.empty();
        console.log('📋 Rendering', this.rooms.length, 'rooms');
        this.rooms.forEach(function (room) {
            console.log('Room:', room.name, 'last_message_date:', room.last_message_date);
            
            var isActive = self.selectedRoom && self.selectedRoom.id === room.id;
            var icon = room.room_type === 'general' ? 'fa-users' : 
                      room.room_type === 'project' ? 'fa-folder' :
                      room.room_type === 'department' ? 'fa-building' : 'fa-user';
            
            var formattedDate = self._formatDate(room.last_message_date);
            console.log('  → Formatted date:', formattedDate);
            
            var $room = $(`
                <div class="o_chat_room_item ${isActive ? 'active' : ''}" data-room-id="${room.id}">
                    <div class="o_chat_room_icon">
                        <i class="fa ${icon}"/>
                    </div>
                    <div class="o_chat_room_info">
                        <div class="o_chat_room_name">${room.name}</div>
                        <div class="o_chat_room_date">${formattedDate || 'Chưa có tin nhắn'}</div>
                    </div>
                    ${room.unread_count > 0 ? `<span class="badge badge-danger">${room.unread_count}</span>` : ''}
                </div>
            `);
            $room.data('room', room);
            $roomList.append($room);
        });
    },
    
    _refreshRoomList: function () {
        var self = this;
        console.log('🔄 Refreshing room list...');
        // Chỉ cập nhật danh sách room, không reload messages
        return this._rpc({
            model: 'chat.room',
            method: 'get_accessible_rooms',
            args: [],
        }).then(function (rooms) {
            console.log('✅ Got rooms:', rooms);
            self.rooms = rooms;
            self._renderRooms();
        }).catch(function(error) {
            console.error('❌ Error refreshing rooms:', error);
        });
    },

    _renderMessages: function () {
        var self = this;
        var $messages = this.$('.o_chat_messages');
        if (!$messages || $messages.length === 0) {
            console.warn('Messages container not found');
            return;
        }
        
        $messages.empty();
        
        // Check if this is announcement room
        var isAnnouncementRoom = this.selectedRoom && this.selectedRoom.is_announcement_room;
        
        this.messages.forEach(function (message) {
            var isMine = self.currentEmployee && message.sender_id[0] === self.currentEmployee.id;
            var messageClass = isMine ? 'o_chat_message_mine' : '';
            
            // Add special style for announcement room messages
            if (isAnnouncementRoom) {
                messageClass += ' o_chat_message_announcement';
            }
            
            var $message = $(`
                <div class="o_chat_message ${messageClass}">
                    <div class="o_chat_message_avatar">
                        <i class="fa ${isAnnouncementRoom ? 'fa-bullhorn' : 'fa-user-circle'}"/>
                    </div>
                    <div class="o_chat_message_content">
                        <div class="o_chat_message_sender">
                            <strong>${message.sender_id[1]}</strong>
                            ${isAnnouncementRoom ? '<span class="badge badge-warning ml-2">THÔNG BÁO</span>' : ''}
                            <span class="o_chat_message_time">${self._formatDate(message.create_date)}</span>
                        </div>
                        <div class="o_chat_message_text">${message.content}</div>
                    </div>
                </div>
            `);
            $messages.append($message);
        });
        $messages.append('<div class="o_messages_end"></div>');
    },
    
    _appendMessages: function (newMessages, isNew) {
        var self = this;
        var $messages = this.$('.o_chat_messages');
        if (!$messages || $messages.length === 0) return;
        
        // Xóa div marker cuối
        $messages.find('.o_messages_end').remove();
        
        // Check if announcement room
        var isAnnouncementRoom = this.selectedRoom && this.selectedRoom.is_announcement_room;
        
        // Append từng tin nhắn mới - chỉ thêm class animated nếu là tin nhắn mới
        newMessages.forEach(function (message) {
            var isMine = self.currentEmployee && message.sender_id[0] === self.currentEmployee.id;
            var messageClass = isMine ? 'o_chat_message_mine' : '';
            
            // Chỉ thêm animation cho tin nhắn thực sự mới
            if (isNew) {
                messageClass += ' o_chat_message_new';
            }
            
            if (isAnnouncementRoom) {
                messageClass += ' o_chat_message_announcement';
            }
            
            var $message = $(`
                <div class="o_chat_message ${messageClass}">
                    <div class="o_chat_message_avatar">
                        <i class="fa ${isAnnouncementRoom ? 'fa-bullhorn' : 'fa-user-circle'}"/>
                    </div>
                    <div class="o_chat_message_content">
                        <div class="o_chat_message_sender">
                            <strong>${message.sender_id[1]}</strong>
                            ${isAnnouncementRoom ? '<span class="badge badge-warning ml-2">THÔNG BÁO</span>' : ''}
                            <span class="o_chat_message_time">${self._formatDate(message.create_date)}</span>
                        </div>
                        <div class="o_chat_message_text">${message.content}</div>
                    </div>
                </div>
            `);
            $messages.append($message);
        });
        
        // Thêm lại marker cuối
        $messages.append('<div class="o_messages_end"></div>');
    },

    _onRoomClick: function (ev) {
        var self = this;
        var $room = $(ev.currentTarget);
        var roomData = $room.data('room');
        
        // Load full room details including is_announcement_room
        this._loadRoomDetails(roomData.id).then(function (fullRoomData) {
            self.selectedRoom = fullRoomData;
            self.messages = [];
            
            // Render chat main area with announcement warning if needed
            var warningHtml = '';
            if (fullRoomData.is_announcement_room) {
                warningHtml = `
                    <div class="alert alert-warning mb-0" style="border-radius: 0;">
                        <i class="fa fa-bullhorn"/> <strong>Phòng Thông Báo:</strong> 
                        Chỉ Ban Quản Lý mới được gửi tin nhắn vào phòng này.
                    </div>
                `;
            }
            
            self.$('.o_chat_main').html(`
                ${warningHtml}
                <div class="o_chat_header">
                    <h4>${fullRoomData.name}</h4>
                </div>
                <div class="o_chat_messages"></div>
                <div class="o_chat_input">
                    <textarea class="form-control" placeholder="Nhập tin nhắn..." rows="2"></textarea>
                    <button class="btn btn-primary" data-action="send">
                        <i class="fa fa-paper-plane"/> Gửi
                    </button>
                </div>
            `);
            
            self._loadMessages();
            self._renderRooms();
        });
    },

    _onSendMessage: function (ev) {
        ev.preventDefault();
        this._sendMessage();
    },

    _onKeyPress: function (ev) {
        if (ev.key === 'Enter' && !ev.shiftKey) {
            ev.preventDefault();
            this._sendMessage();
        }
    },

    _onRefresh: function () {
        this._refreshRoomList();
    },

    _sendMessage: function () {
        var self = this;
        var $textarea = this.$('.o_chat_input textarea');
        var content = $textarea.val().trim();
        
        if (!content) {
            console.warn('Nội dung tin nhắn trống');
            return;
        }
        
        if (!this.selectedRoom) {
            console.error('Chưa chọn phòng chat');
            this.displayNotification({
                title: 'Lỗi',
                message: 'Vui lòng chọn phòng chat trước',
                type: 'warning',
            });
            return;
        }
        
        if (!this.currentEmployee) {
            console.error('Không tìm thấy nhân viên hiện tại');
            this.displayNotification({
                title: 'Lỗi',
                message: 'Bạn chưa có thông tin nhân viên. Vui lòng liên hệ quản trị viên.',
                type: 'danger',
            });
            return;
        }
        
        console.log('Gửi tin nhắn:', {
            room_id: this.selectedRoom.id,
            sender_id: this.currentEmployee.id,
            content: content,
        });
        
        return this._rpc({
            model: 'chat.message',
            method: 'create',
            args: [{
                room_id: this.selectedRoom.id,
                sender_id: this.currentEmployee.id,
                content: content,
                message_type: 'text',
            }],
        }).then(function (messageId) {
            console.log('Tin nhắn đã gửi thành công, ID:', messageId);
            $textarea.val('');
            return self._loadMessages();
        }).catch(function (error) {
            console.error('Lỗi khi gửi tin nhắn:', error);
            self.displayNotification({
                title: 'Lỗi',
                message: error.data && error.data.message ? error.data.message : 'Không thể gửi tin nhắn',
                type: 'danger',
            });
        });
    },

    _scrollToBottom: function () {
        var $messages = this.$('.o_chat_messages');
        if ($messages && $messages.length > 0) {
            $messages.scrollTop($messages[0].scrollHeight);
        }
    },
    
    _debouncedScrollToBottom: function () {
        var self = this;
        if (this._scrollTimeout) {
            clearTimeout(this._scrollTimeout);
        }
        this._scrollTimeout = setTimeout(function () {
            var $messages = self.$('.o_chat_messages');
            if ($messages && $messages.length > 0) {
                // Kiểm tra xem user có đang scroll ở gần cuối không
                var scrollPos = $messages.scrollTop();
                var scrollHeight = $messages[0].scrollHeight;
                var clientHeight = $messages[0].clientHeight;
                
                // Chỉ auto scroll nếu user đang ở gần cuối (trong vòng 100px)
                if (scrollHeight - scrollPos - clientHeight < 100) {
                    $messages.animate({scrollTop: scrollHeight}, 200);
                }
            }
        }, 100);
    },

    _formatDate: function (dateStr) {
        if (!dateStr) return "";
        
        var date = new Date(dateStr);
        
        // Kiểm tra ngày có hợp lệ không
        if (isNaN(date.getTime())) {
            console.warn('Invalid date:', dateStr);
            return "";
        }
        
        var now = new Date();
        var diffMs = now - date;
        var diffMins = Math.floor(diffMs / 60000);
        var diffHours = Math.floor(diffMs / 3600000);
        var diffDays = Math.floor(diffMs / 86400000);
        
        // Vừa xong (< 1 phút)
        if (diffMins < 1) {
            return 'Vừa xong';
        }
        
        // X phút trước (< 60 phút)
        if (diffMins < 60) {
            return diffMins + ' phút trước';
        }
        
        // X giờ trước (< 24 giờ)
        if (diffHours < 24) {
            return diffHours + ' giờ trước';
        }
        
        // X ngày trước (< 7 ngày)
        if (diffDays < 7) {
            return diffDays + ' ngày trước';
        }
        
        // Với ngày cũ hơn: dd/mm/yyyy
        var day = date.getDate().toString().padStart(2, '0');
        var month = (date.getMonth() + 1).toString().padStart(2, '0');
        var year = date.getFullYear();
        return day + '/' + month + '/' + year;
    },
});

core.action_registry.add('chat_noi_bo.chat_window', ChatWindow);

return ChatWindow;

});
