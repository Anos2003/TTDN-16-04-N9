#!/bin/bash

# Script để upload các module lên GitHub
# Repository: https://github.com/danganh1009/TTDN-16-04-N9.git

echo "Đang cấu hình git repository..."

# Khởi tạo git nếu chưa có
if [ ! -d ".git" ]; then
    git init
    echo "Đã khởi tạo git repository"
fi

# Thêm remote
git remote remove origin 2>/dev/null
git remote add origin https://github.com/danganh1009/TTDN-16-04-N9.git

# Tạo .gitignore
cat > .gitignore << 'EOF'
*.pyc
*.pyo
__pycache__/
*.swp
*.swo
*~
.DS_Store
*.log
EOF

# Thêm tất cả các file
git add .

# Commit
git commit -m "Upload các module: nhân sự, dự án, công việc, thông báo, chat nội bộ và AI chatbot"

# Push lên GitHub
echo "Đang push lên GitHub..."
git branch -M main
git push -u origin main --force

echo "Hoàn tất!"
