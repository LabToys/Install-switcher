#!/usr/bin/env python3
import os
import time
import subprocess
import sys
import warnings
from collections import deque

# Configuration
VENV_PATH = "/opt/auto_switcher_venv"
CONFIG = {
    "resolution": "1920x1080",
    "framerate": 30,
    "cameras": [
        {"video": "/dev/video0", "audio": "hw:1,0", "name": "CAM1"},
        {"video": "/dev/video2", "audio": "hw:2,0", "name": "CAM2"},
        {"video": "/dev/video4", "audio": "hw:3,0", "name": "CAM3"},
        {"video": "/dev/video6", "audio": "hw:4,0", "name": "CAM4"}
    ],
    "silence_threshold": 0.1,
    "hold_time": 2.5,
    "font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "recording_dir": "/recordings"
}

def ensure_dependencies():
    """Install all required system and Python dependencies"""
    print("🔧 Installing dependencies...")
    
    # Install system packages
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", 
                   "ffmpeg", "v4l2loopback-dkms", "alsa-utils",
                   "python3-pip", "python3-dev", "python3-venv",
                   "build-essential"])
    
    # Create virtual environment
    if not os.path.exists(VENV_PATH):
        subprocess.run(["sudo", "python3", "-m", "venv", VENV_PATH])
    
    # Install Python packages using the venv's pip
    pip_path = f"{VENV_PATH}/bin/pip"
    subprocess.run([pip_path, "install", "numpy", "webrtcvad-wheels"])

class AutoSwitcher:
    def __init__(self):
        # Try importing dependencies
        try:
            from webrtcvad import Vad
            self.vad = Vad(2)
            self.use_vad = True
        except ImportError:
            print("⚠️ Using fallback audio detection (webrtcvad not available)")
            self.use_vad = False
            import numpy as np
            self.np = np
            
        self.current_cam = 0
        self.ffmpeg = None
        self.last_switch = time.time()
        
        if not os.path.exists("/etc/auto_switcher_installed"):
            self.first_run_setup()
        
        self.initialize_system()

    def first_run_setup(self):
        """System initialization"""
        print("⚡ Running first-time setup...")
        
        # Create virtual camera
        self.create_virtual_camera()
        
        # Create recording directory
        os.makedirs(CONFIG["recording_dir"], exist_ok=True)
        subprocess.run(["sudo", "chown", "-R", "pi:pi", CONFIG["recording_dir"]])
        
        # Create systemd service
        self.create_systemd_service()
        
        # Mark installation complete
        with open("/etc/auto_switcher_installed", "w") as f:
            f.write("1")
        
        print("✅ First-time setup complete! Rebooting...")
        subprocess.run(["sudo", "reboot"])
        sys.exit(0)

    def create_virtual_camera(self):
        """Create persistent /dev/video100"""
        subprocess.run(["sudo", "modprobe", "-r", "v4l2loopback"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "modprobe", "v4l2loopback", 
                       "devices=1", "video_nr=100", "card_label=AutoSwitcher"])
        
        # Make persistent
        with open("/etc/modprobe.d/v4l2loopback.conf", "w") as f:
            f.write("options v4l2loopback devices=1 video_nr=100 card_label=AutoSwitcher\n")
        subprocess.run(["sudo", "sh", "-c", "echo v4l2loopback > /etc/modules-load.d/v4l2loopback.conf"])

    def create_systemd_service(self):
        """Create auto-start service"""
        service = f"""
[Unit]
Description=Auto Camera Switcher
After=network.target

[Service]
User=pi
ExecStart={VENV_PATH}/bin/python {os.path.abspath(__file__)}
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
"""
        with open("/etc/systemd/system/auto-switcher.service", "w") as f:
            f.write(service)
        
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        subprocess.run(["sudo", "systemctl", "enable", "auto-switcher.service"])

    def initialize_system(self):
        """Initialize hardware"""
        # Set all cameras to MJPG 1080p30
        for cam in CONFIG["cameras"]:
            subprocess.run([
                "v4l2-ctl", "-d", cam["video"],
                "--set-fmt-video", f"width=1920,height=1080,pixelformat=MJPG",
                "--set-parm", "30"
            ], stderr=subprocess.DEVNULL)

        # Clear HDMI output
        subprocess.run(["setterm", "-cursor", "off"])
        subprocess.run(["dd", "if=/dev/zero", "of=/dev/fb0", "bs=1M"], stderr=subprocess.DEVNULL)

    def get_audio_level(self, device_idx):
        """Measure audio level with fallback methods"""
        if self.use_vad:
            # Use webrtcvad if available
            try:
                audio = subprocess.run([
                    "arecord", "-D", CONFIG["cameras"][device_idx]["audio"],
                    "-d", "0.1", "-f", "S16_LE", "-r", "16000",
                    "-c", "1", "-t", "raw"
                ], capture_output=True).stdout
                return int(self.vad.is_speech(audio, 16000))
            except:
                return 0
        else:
            # Fallback to numpy-based RMS calculation
            try:
                output = subprocess.run([
                    "arecord", "-D", CONFIG["cameras"][device_idx]["audio"],
                    "-d", "0.1", "-f", "S16_LE", "-t", "raw"
                ], capture_output=True).stdout
                if output:
                    audio_data = self.np.frombuffer(output, dtype=self.np.int16)
                    rms = self.np.sqrt(self.np.mean(self.np.square(audio_data))) / 32768.0
                    return rms
                return 0
            except:
                return 0

    def start_stream(self):
        if self.ffmpeg:
            self.ffmpeg.terminate()
            time.sleep(0.3)

        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-f", "v4l2", "-input_format", "mjpeg",
            "-video_size", CONFIG["resolution"],
            "-framerate", str(CONFIG["framerate"]),
            "-i", CONFIG["cameras"][self.current_cam]["video"],
            "-f", "alsa", "-ac", "2",
            "-i", CONFIG["cameras"][self.current_cam]["audio"],
            "-filter_complex",
            f"[0:v]format=rgb565le,"
            f"drawtext=fontfile={CONFIG['font']}:"
            f"text='{CONFIG['cameras'][self.current_cam]['name']}':"
            "x=20:y=20:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.5[hdmi];"
            "[1:a]volume=2.0[audio]",
            "-map", "[hdmi]",
            "-f", "fbdev", "-pix_fmt", "rgb565le", "/dev/fb0",
            "-map", "[audio]",
            "-f", "segment", "-segment_time", "300",
            "-strftime", "1", "-c:a", "aac", "-b:a", "192k",
            os.path.join(CONFIG["recording_dir"], "rec_%Y%m%d_%H%M%S.mp4")
        ]
        self.ffmpeg = subprocess.Popen(cmd)
        print(f"Switched to {CONFIG['cameras'][self.current_cam]['name']}")

    def run(self):
        try:
            while True:
                levels = [self.get_audio_level(i) for i in range(4)]
                loudest = max(levels)
                
                if loudest > CONFIG["silence_threshold"]:
                    new_cam = levels.index(loudest)
                else:
                    new_cam = 0
                
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
    if os.geteuid() != 0:
        print("❌ Please run with sudo!")
        sys.exit(1)
    
    # If not in virtual environment, re-execute using venv
    if sys.prefix != VENV_PATH:
        ensure_dependencies()
        print("🔁 Restarting in virtual environment...")
        os.execl(f"{VENV_PATH}/bin/python", f"{VENV_PATH}/bin/python", *sys.argv)
    
    # Now running in virtual environment
    switcher = AutoSwitcher()
    switcher.start_stream()
    switcher.run()
