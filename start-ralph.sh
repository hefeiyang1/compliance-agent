#!/bin/bash

echo "========================================"
echo "Starting Ralph for Compliance Agent..."
echo "========================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo ""

echo "Starting Ralph with monitoring..."
echo "========================================"
echo ""

# 启动 Ralph
ralph --monitor

echo ""
echo "========================================"
echo "Ralph stopped."
