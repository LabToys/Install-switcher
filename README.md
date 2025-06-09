🎥 Raspberry Pi Auto Camera Switcher
Automatic 1080p30 video switching with audio-activated camera selection
(Outputs to /dev/video100 )

[![MIT License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-5.1+-green.svg?logo=ffmpeg)](https://ffmpeg.org/)
[![ALSA](https://img.shields.io/badge/ALSA-1.2-red.svg?logo=alsa)](https://alsa-project.org/)
[![v4l2loopback](https://img.shields.io/badge/v4l2loopback-0.12-blue.svg)](https://github.com/umlaeute/v4l2loopback)
<img src="https://www.raspberrypi.com/app/uploads/2022/02/COLOUR-Raspberry-Pi-Symbol-Registered.png" width="120">
  
📦 Installation
1.
git clone https://github.com/LabToys/Install-switcher.git && cd Install-switcher && chmod +x install_switcher.sh && sudo ./install_switcher.sh

2.
sudo python3 auto_switcher_1080p.py 


Installs:
FFmpeg & ALSA utilities
v4l2loopback kernel module
Python dependencies (WebRTC VAD)

Auto-starts on boot via systemd
Voice Activity Detection (WebRTC)
Clean 1080p30 output
Camera labels overlay
