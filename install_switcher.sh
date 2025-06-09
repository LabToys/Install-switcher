#!/bin/bash
# 1080p30 Auto-Switcher Installer
# Official installation script for LabToys/Install-switcher

echo "🔧 Installing dependencies..."
sudo apt update
sudo apt install -y ffmpeg v4l2loopback-dkms alsa-utils python3-webrtcvad

echo "🚀 Creating virtual 1080p hdmi out..."
sudo modprobe -r v4l2loopback 2>/dev/null
sudo modprobe v4l2loopback devices=1 video_nr=100 card_label="HDMI_OUT_1080p" exclusive_caps=1

echo "📥 Downloading 1080p switcher..."
sudo wget -O /usr/local/bin/auto_switcher_1080p.py \
  https://raw.githubusercontent.com/LabToys/Install-switcher/main/auto_switcher_1080p.py
sudo chmod +x /usr/local/bin/auto_switcher_1080p.py

echo "🔄 Creating systemd service..."
sudo bash -c 'cat > /etc/systemd/system/auto-switcher_1080p.service <<EOF
[Unit]
Description=1080p30 Auto Switcher
After=network.target sound.target

[Service]
User=pi
ExecStart=/usr/bin/python3 /usr/local/bin/auto_switcher_1080p.py
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"
WorkingDirectory=/home/pi

[Install]
WantedBy=multi-user.target
EOF'

echo "⚙️ Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable auto-switcher_1080p.service

echo "🎉 Installation complete! Starting service..."
sudo systemctl start auto-switcher_1080p.service

echo -e "\n✅ 1080p30 Switcher Installed!"
echo "Virtual Camera: /dev/video100"
echo "View logs: journalctl -u auto-switcher_1080p.service -f"
