#!/bin/bash
cd /app/
# 不使用虚拟环境，直接使用系统Python（已在Dockerfile中安装依赖）
# source install.sh
python3 main.py -job True -init True