🎥 Raspberry Pi Auto Camera Switcher
Automatic 1080p30 video switching with audio-activated camera selection
(Outputs to /dev/video100 in YUV420)

[![MIT License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-5.1+-green.svg?logo=ffmpeg)](https://ffmpeg.org/)
[![ALSA](https://img.shields.io/badge/ALSA-1.2-red.svg?logo=alsa)](https://alsa-project.org/)
[![v4l2loopback](https://img.shields.io/badge/v4l2loopback-0.12-blue.svg)](https://github.com/umlaeute/v4l2loopback)

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
