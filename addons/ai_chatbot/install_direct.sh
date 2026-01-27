#!/bin/bash
# Script cài đặt AI Chatbot qua command line

echo "🤖 Installing AI Chatbot Assistant..."
echo "======================================"

# Check Odoo config
if [ ! -f "/etc/odoo/odoo.conf" ]; then
    echo "❌ Không tìm thấy /etc/odoo/odoo.conf"
    exit 1
fi

# Get database name
DB_NAME=$(grep "^db_name" /etc/odoo/odoo.conf | cut -d'=' -f2 | tr -d ' ' || echo "danganh1009")

echo "📊 Database: $DB_NAME"
echo ""

# Option 1: Install via odoo-bin
echo "Cách 1: Cài qua odoo-bin (khuyến nghị)"
echo "======================================="
echo "odoo-bin -c /etc/odoo/odoo.conf -d $DB_NAME -i ai_chatbot --stop-after-init"
echo ""

# Option 2: SQL direct install
echo "Cách 2: Cài trực tiếp qua SQL"
echo "=============================="
echo "psql -U odoo -d $DB_NAME -c \"INSERT INTO ir_module_module (name, state) VALUES ('ai_chatbot', 'to install') ON CONFLICT (name) DO UPDATE SET state = 'to install';\""
echo ""

# Check if we can run odoo-bin
if command -v odoo-bin &> /dev/null; then
    echo "✅ Tìm thấy odoo-bin"
    echo ""
    read -p "Bạn có muốn cài ngay không? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Đang cài đặt..."
        odoo-bin -c /etc/odoo/odoo.conf -d $DB_NAME -i ai_chatbot --stop-after-init
        echo ""
        echo "✅ Hoàn thành! Hãy restart Odoo:"
        echo "   sudo systemctl restart odoo"
    fi
else
    echo "⚠️  Không tìm thấy odoo-bin"
    echo "    Hãy chạy lệnh thủ công ở trên"
fi
