# py-image-downloader

# 创建虚拟环境 (venv)
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装必要的库
pip install requests

# 运行
python3 main.py

# 导出当前环境的所有库
pip freeze > requirements.txt

# 安装所有库
pip install -r requirements.txt