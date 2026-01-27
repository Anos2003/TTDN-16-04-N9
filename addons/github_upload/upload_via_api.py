#!/usr/bin/env python3
"""
Script upload các module lên GitHub qua API
Cần GitHub Personal Access Token
"""

import os
import base64
import json
import requests
from pathlib import Path

# Cấu hình
GITHUB_TOKEN = input("Nhập GitHub Personal Access Token: ").strip()
REPO_OWNER = "danganh1009"
REPO_NAME = "TTDN-16-04-N9"
BRANCH = "main"

BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_file(file_path, content, message="Upload file"):
    """Upload một file lên GitHub"""
    url = f"{BASE_URL}/contents/{file_path}"
    
    # Kiểm tra file đã tồn tại chưa
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json()["sha"]
    
    data = {
        "message": message,
        "content": base64.b64encode(content).decode('utf-8'),
        "branch": BRANCH
    }
    
    if sha:
        data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✓ Uploaded: {file_path}")
        return True
    else:
        print(f"✗ Failed: {file_path} - {response.json()}")
        return False

def upload_directory(local_dir, remote_path=""):
    """Upload toàn bộ thư mục"""
    local_dir = Path(local_dir)
    
    for item in local_dir.rglob("*"):
        if item.is_file():
            # Bỏ qua các file không cần thiết
            if item.suffix in ['.pyc', '.pyo'] or item.name == '.DS_Store':
                continue
            if '__pycache__' in str(item):
                continue
                
            relative_path = item.relative_to(local_dir.parent)
            remote_file_path = str(relative_path).replace('\\', '/')
            
            try:
                with open(item, 'rb') as f:
                    content = f.read()
                upload_file(remote_file_path, content, f"Upload {relative_path}")
            except Exception as e:
                print(f"Error uploading {item}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("UPLOAD CÁC MODULE LÊN GITHUB")
    print("=" * 60)
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Branch: {BRANCH}")
    print()
    print("Lưu ý: Bạn cần tạo Personal Access Token tại:")
    print("https://github.com/settings/tokens")
    print("Với quyền: repo (full control)")
    print("=" * 60)
    print()
    
    current_dir = Path(__file__).parent
    
    modules = [
        'nhan_su',
        'quan_ly_du_an', 
        'quan_ly_cong_viec',
        'thong_bao',
        'chat_noi_bo',
        'ai_chatbot'
    ]
    
    # Upload README
    readme_path = current_dir / 'README.md'
    if readme_path.exists():
        with open(readme_path, 'rb') as f:
            upload_file('README.md', f.read(), "Add README")
    
    # Upload các module
    for module in modules:
        module_dir = current_dir / module
        if module_dir.exists():
            print(f"\nUploading module: {module}")
            upload_directory(module_dir, module)
    
    print("\n" + "=" * 60)
    print("HOÀN TẤT!")
    print("=" * 60)
