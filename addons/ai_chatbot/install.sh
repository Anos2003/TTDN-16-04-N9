#!/bin/bash
# Script cài đặt AI Chatbot cho Odoo 15

echo "🤖 Cài đặt AI Chatbot Assistant"
echo "================================"

# 1. Check module exists
if [ ! -d "/mnt/extra-addons/ai_chatbot" ]; then
    echo "❌ Module ai_chatbot không tồn tại!"
    exit 1
fi

echo "✅ Module ai_chatbot tồn tại"

# 2. Check Python syntax
echo ""
echo "Kiểm tra syntax Python..."
cd /mnt/extra-addons/ai_chatbot
python3 -m py_compile __init__.py __manifest__.py models/*.py controllers/*.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax OK"
else
    echo "❌ Lỗi syntax Python!"
    exit 1
fi

# 3. Instructions
echo ""
echo "📋 Các bước tiếp theo:"
echo "====================="
echo ""
echo "1️⃣  RESTART ODOO SERVER:"
echo "   sudo systemctl restart odoo"
echo ""
echo "2️⃣  UPDATE APPS LIST (trong Odoo UI):"
echo "   Apps → Click ⋮ (góc phải) → Update Apps List"
echo ""
echo "3️⃣  INSTALL MODULE:"
echo "   Apps → Tìm 'AI Chatbot' → Click Install"
echo ""
echo "4️⃣  SỬ DỤNG:"
echo "   Chat Nội Bộ → Chọn phòng chat → Tab '🤖 AI Assistant'"
echo ""
echo "💡 Gõ @ai trước câu hỏi để chat với AI!"
echo ""
