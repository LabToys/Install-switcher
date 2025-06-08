🎥 Raspberry Pi Auto Camera Switcher
Automatic 1080p30 video switching with audio-activated camera selection
(Outputs to /dev/video100 in YUV420)

[![MIT License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-5.1+-green.svg?logo=ffmpeg)](https://ffmpeg.org/)
[![ALSA](https://img.shields.io/badge/ALSA-1.2-red.svg?logo=alsa)](https://alsa-project.org/)
[![v4l2loopback](https://img.shields.io/badge/v4l2loopback-0.12-blue.svg)](https://github.com/umlaeute/v4l2loopback)


<div align="center">
  <img src="https://www.raspberrypi.com/app/uploads/2022/02/COLOUR-Raspberry-Pi-Symbol-Registered.png" width="120"><div align="center">
  <img src="https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/ffmpeg-logo.svg" width="120" alt="FFmpeg" style="background:#008000;padding:10px">
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/ea/HDMI_logo.png" width="120" alt="HDMI">
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" width="60" alt="Python">
</div>

## 🛠️ Tech Stack
| Component | HD Logo | Version |
|-----------|---------|---------|
| **Raspberry Pi** | <img src="https://www.raspberrypi.com/app/uploads/2022/02/COLOUR-Raspberry-Pi-Symbol-Registered.png" width="80"> | 4B/5 |
| **FFmpeg** | <img src="https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/ffmpeg-logo.svg" width="80" style="background:#008000;padding:5px"> | 5.1+ |
| **HDMI** | <img src="https://upload.wikimedia.org/wikipedia/commons/e/ea/HDMI_logo.png" width="80"> | 2.0 |
| **ALSA** | <img src="https://www.alsa-project.org/alsa/img/alsa-logo.png" width="80"> | 1.2+ |
| **v4l2loopback** | <img src="https://raw.githubusercontent.com/umlaeute/v4l2loopback/master/doc/v4l2loopback.png" width="80"> | 0.12+ |

## 🌟 Features
<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/ea/HDMI_logo.png" width="120" alt="HDMI Output">

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
