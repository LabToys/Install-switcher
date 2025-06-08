Raspberry Pi Auto Camera Switcher
Automatic 1080p30 video switching based on audio input with YUV420 pipeline

📥 Installation

bash
# 1. Make the installer executable
chmod +x install_switcher.sh

# 2. Run the installer (requires sudo)
sudo ./install_switcher.sh
The installer will:

Install dependencies (FFmpeg, v4l2loopback, WebRTC VAD)
Create virtual camera at /dev/video100
Configure automatic startup on boot
✅ Verification

Check Virtual Camera Format

bash
v4l2-ctl -d /dev/video100 --get-fmt-video
Expected output:

text
Pixel Format: 'YU12' (Planar YUV 4:2:0)
Width/Height: 1920/1080
Field: None
[...]
Test Live Output

bash
ffplay -f v4l2 -video_size 1920x1080 -pixel_format yuv420p /dev/video100
Press q to exit the preview.

Check Service Status

bash
systemctl status auto-switcher.service
Healthy output should show:

text
Active: active (running) since [...]
Main PID: [...] (python3)
🔍 View Logs

bash
# Follow live logs:
journalctl -u auto-switcher.service -f

# View full boot logs:
journalctl -u auto-switcher.service -b
🛠️ Troubleshooting

If /dev/video100 doesn't appear:

bash
# Reload kernel module
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback video_nr=100

# Verify creation
ls -l /dev/video100
If service fails to start:

bash
# Check for errors
sudo systemctl restart auto-switcher.service
journalctl -u auto-switcher.service -p 3 -xb
🚀 Usage

The switcher will automatically:

Select camera with loudest audio input
Fall back to Camera 1 when idle
Output to /dev/video100 in 1080p30 YUV420
Use the virtual camera with:

OBS Studio
Zoom/Teams (via v4l2loopback)
FFmpeg pipelines
