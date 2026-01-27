#!/bin/bash
# Script clear cache và chuẩn bị nâng cấp module Odoo

echo "========================================"
echo "  CLEAR CACHE VÀ CHUẨN BỊ NÂNG CẤP"
echo "========================================"
echo ""

# 1. Xóa Python cache
echo "1️⃣  Xóa Python cache files..."
find /mnt/extra-addons/nhan_su -name "*.pyc" -delete 2>/dev/null
find /mnt/extra-addons/quan_ly_du_an -name "*.pyc" -delete 2>/dev/null
find /mnt/extra-addons/quan_ly_cong_viec -name "*.pyc" -delete 2>/dev/null
find /mnt/extra-addons/thong_bao -name "*.pyc" -delete 2>/dev/null

find /mnt/extra-addons/nhan_su -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /mnt/extra-addons/quan_ly_du_an -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /mnt/extra-addons/quan_ly_cong_viec -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /mnt/extra-addons/thong_bao -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "   ✅ Đã xóa Python cache"
echo ""

# 2. Kiểm tra file XML
echo "2️⃣  Kiểm tra file XML..."
python3 /mnt/extra-addons/test_xml_validation.py
echo ""

# 3. Hướng dẫn tiếp theo
echo "========================================"
echo "  ĐÃ HOÀN TẤT CHUẨN BỊ!"
echo "========================================"
echo ""
echo "📌 BƯỚC TIẾP THEO:"
echo ""
echo "Trong trình duyệt Odoo:"
echo "  1. Nhấn Ctrl + Shift + Delete để xóa cache trình duyệt"
echo "  2. Reload trang (F5)"
echo "  3. Vào Settings → Apps → Update Apps List"
echo "  4. Tìm module và nhấn Upgrade"
echo ""
echo "Hoặc restart Odoo service:"
echo "  sudo systemctl restart odoo"
echo "  # hoặc"
echo "  docker restart <container-name>"
echo ""
echo "Nếu vẫn lỗi, chạy nâng cấp qua CLI:"
echo "  odoo-bin -u quan_ly_du_an -d <database> --stop-after-init"
echo ""
echo "========================================"
