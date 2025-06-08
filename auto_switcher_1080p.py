#!/usr/bin/env python3
import os
import time
import subprocess
import webrtcvad
import warnings
from collections import deque

# Suppress warnings
warnings.filterwarnings("ignore")

# Configuration - PRESERVE FILENAME BUT IMPROVE FUNCTIONALITY
CONFIG = {
    # Video Input (MJPG)
    "resolution": "1920x1080",
    "framerate": 30,
    "cameras": [
        {"video": "/dev/video0", "audio": "hw:1,0", "name": "CAM1"},
        {"video": "/dev/video2", "audio": "hw:2,0", "name": "CAM2"},
        {"video": "/dev/video4", "audio": "hw:3,0", "name": "CAM3"},
        {"video": "/dev/video6", "audio": "hw:4,0", "name": "CAM4"}
    ],
    
    # Audio Switching
    "vad_level": 2,          # 1-3 (higher = more strict)
    "silence_threshold": -45, # dB level for silence
    "hold_time": 2.5,        # seconds before reverting to CAM1
    
    # Output
    "font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "recording_dir": "/recordings",
    "recording_duration": 300  # Split recordings every 5 minutes
}

class AutoSwitcher:
    def __init__(self):
        self.vad = webrtcvad.Vad(CONFIG["vad_level"])
        self.current_cam = 0  # Default to CAM1
        self.ffmpeg = None
        self.last_switch = time.time()
        self.setup_system()

    def setup_system(self):
        """Initialize hardware and directories"""
        os.makedirs(CONFIG["recording_dir"], exist_ok=True)
        
        # Force MJPG 1080p30 on all cameras
        for cam in CONFIG["cameras"]:
            subprocess.run([
                "v4l2-ctl", "-d", cam["video"],
                "--set-fmt-video", "width=1920,height=1080,pixelformat=MJPG",
                "--set-parm", "30"
            ], stderr=subprocess.DEVNULL)
        
        # Clear HDMI output
        subprocess.run(["dd", "if=/dev/zero", "of=/dev/fb0", "bs=1M"], stderr=subprocess.DEVNULL)
        subprocess.run(["setterm", "-cursor", "off"])

    def get_audio_level(self, device_idx):
        """Get RMS level in dB using FFmpeg's astats"""
        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-f", "alsa", "-i", CONFIG["cameras"][device_idx]["audio"],
            "-af", "astats=measure_perchannel=none:measure_overall=RMS_level",
            "-f", "null", "-"
        ]
        try:
            output = subprocess.run(cmd, capture_output=True, text=True, timeout=0.2).stderr
            return float(output.split("RMS_level dB: ")[-1].split()[0])
        except:
            return -99  # Return very quiet level if error

    def start_stream(self):
        if self.ffmpeg:
            self.ffmpeg.terminate()
            time.sleep(0.3)  # Allow clean transition

        # FFmpeg pipeline: MJPG→RGB565LE HDMI + MP4 recording
        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-f", "v4l2",
            "-input_format", "mjpeg",
            "-video_size", CONFIG["resolution"],
            "-framerate", str(CONFIG["framerate"]),
            "-i", CONFIG["cameras"][self.current_cam]["video"],
            "-f", "alsa",
            "-ac", "2",
            "-i", CONFIG["cameras"][self.current_cam]["audio"],
            "-filter_complex",
            f"[0:v]format=rgb565le,"
            f"drawtext=fontfile={CONFIG['font']}:"
            f"text='{CONFIG['cameras'][self.current_cam]['name']}':"
            "x=20:y=20:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.5[hdmi];"
            "[1:a]volume=2.0[audio]",
            "-map", "[hdmi]",
            "-f", "fbdev",
            "-pix_fmt", "rgb565le",
            "/dev/fb0",
            "-map", "[audio]",
            "-f", "segment",
            "-segment_time", str(CONFIG["recording_duration"]),
            "-strftime", "1",
            "-c:a", "aac",
            "-b:a", "192k",
            os.path.join(CONFIG["recording_dir"], "rec_%Y%m%d_%H%M%S.mp4")
        ]

        self.ffmpeg = subprocess.Popen(cmd)
        print(f"Switched to {CONFIG['cameras'][self.current_cam]['name']}")

    def run(self):
        try:
            while True:
                # Get all audio levels
                levels = [self.get_audio_level(i) for i in range(4)]
                loudest = max(levels)
                
                # Switch logic
                if loudest > CONFIG["silence_threshold"]:
                    new_cam = levels.index(loudest)
                else:
                    new_cam = 0  # Fallback to CAM1
                
                if new_cam != self.current_cam:
                    self.current_cam = new_cam
                    self.last_switch = time.time()
                    self.start_stream()
                
                time.sleep(0.1)
                
        finally:
            if self.ffmpeg:
                self.ffmpeg.terminate()
            subprocess.run(["setterm", "-cursor", "on"])

if __name__ == "__main__":
    # Create systemd service (preserving filename)
    service_file = """
[Unit]
Description=Auto Switcher (1080p MJPG→RGB565LE)
After=network.target

[Service]
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/auto_switcher_1080p.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""
    with open("/etc/systemd/system/auto-switcher.service", "w") as f:
        f.write(service_file)
    
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "auto-switcher.service"])
    
    # Start the switcher
    switcher = AutoSwitcher()
    switcher.start_stream()
    switcher.run()
