🎥 Raspberry Pi Auto Camera Switcher
Automatic 1080p30 video switching with audio-activated camera selection
(Outputs to /dev/video100 in YUV420)

https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/Python-3-blue.svg

📦 Installation

1. Clone the repository

bash
git clone https://github.com/LabToys/Install-switcher.git
cd Install-switcher
2. Run the installer

bash
chmod +x install_switcher.sh
sudo ./install_switcher.sh
Installs:

FFmpeg & ALSA utilities
v4l2loopback kernel module
Python dependencies (WebRTC VAD)
🔧 Configuration

Edit auto_switcher_1080p.py to customize:

python
CONFIG = {
    "resolution": "1920x1080",  # Output resolution
    "framerate": 30,            # Frame rate
    "audio_devices": ["hw:1,0", "hw:2,0", ...],  # ALSA inputs
    "video_devices": ["/dev/video0", "/dev/video2", ...],  # Camera paths
    "virtual_cam": "/dev/video100"  # Virtual output device
}
🚀 Usage

bash
# Manual start (if not using systemd)
python3 /usr/local/bin/auto_switcher_1080p.py
Features:

Auto-starts on boot via systemd
Voice Activity Detection (WebRTC)
Clean 1080p30 YUV420 output
Camera labels overlay
