#!/bin/bash
set -e

echo "========================================================================"
echo "IMPORTANT: For GPU acceleration, you must manually install"
echo "NVIDIA CUDA Toolkit and cuDNN library first."
echo "See: https://developer.nvidia.com/cuda-toolkit"
echo "See: https://developer.nvidia.com/cudnn"
echo ""
echo "This program also requires 'xdotool' for text input."
echo "Please install it using your system's package manager."
echo "e.g., sudo apt-get install xdotool  OR  sudo pacman -S xdotool"
echo "========================================================================"
echo ""

echo "--- Installing Python dependencies ---"
uv sync

echo ""
echo "--- Installation complete! ---"