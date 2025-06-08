#!/usr/bin/env python3
import os
import time
import subprocess
import webrtcvad
import numpy as np
from collections import deque

# 1080p30 YUV420 Configuration
CONFIG = {
    "resolution": "1920x1080",
    "framerate": "30",
    "pixel_format": "yuv420p",
    "audio_devices": ["hw:1,0", "hw:2,0", "hw:3,0", "hw:4,0"],
    "video_devices": ["/dev/video0", "/dev/video2", "/dev/video4", "/dev/video6"],
    "virtual_cam": "/dev/video100",
    "vad_level": 2,  # WebRTC VAD aggressiveness (1-3)
    "hold_time": 2.5  # Seconds before reverting to main cam
}

class Switcher1080p:
    def __init__(self):
        self.vad = webrtcvad.Vad(CONFIG["vad_level"])
        self.current_cam = 0  # Main camera as default
        self.ffmpeg = None
        
    def ensure_yuv420(self, device):
        """Verify and enforce YUV420 input"""
        cmd = [
            "v4l2-ctl", "-d", device,
            "--set-fmt-video", 
            f"width={CONFIG['resolution'].split('x')[0]}," 
            f"height={CONFIG['resolution'].split('x')[1]}," 
            f"pixelformat={CONFIG['pixel_format']}"
        ]
        subprocess.run(cmd, check=True)

    def start_stream(self):
        if self.ffmpeg:
            self.ffmpeg.terminate()
            time.sleep(0.2)
        
        # Enforce YUV420 on input
        self.ensure_yuv420(CONFIG["video_devices"][self.current_cam])
        
        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-f", "v4l2",
            "-input_format", CONFIG["pixel_format"],
            "-video_size", CONFIG["resolution"],
            "-framerate", CONFIG["framerate"],
            "-i", CONFIG["video_devices"][self.current_cam],
            "-f", "alsa",
            "-ac", "2",
            "-i", CONFIG["audio_devices"][self.current_cam],
            "-vf", "format=yuv420p,drawtext=text='CAM %{n}':x=20:y=20:fontsize=36:box=1:boxcolor=black@0.5",
            "-f", "v4l2",
            "-pix_fmt", CONFIG["pixel_format"],
            CONFIG["virtual_cam"]
        ]
        self.ffmpeg = subprocess.Popen(cmd)
        print(f"Switched to CAM{self.current_cam+1} (1080p30 YUV420)")

    def run(self):
        try:
            while True:
                # Voice detection logic
                active_cams = [
                    i for i in range(4)
                    if self.vad.is_speech(
                        subprocess.run(
                            ["arecord", "-D", CONFIG["audio_devices"][i],
                            "-d", "0.1", "-f", "S16_LE", "-r", "16000",
                            "-c", "1", "-t", "raw"],
                            capture_output=True
                        ).stdout,
                        16000
                    )
                ]
                
                if active_cams:
                    new_cam = active_cams[0]  # Prioritize lower-numbered cams
                    if new_cam != self.current_cam:
                        self.current_cam = new_cam
                        self.start_stream()
                elif self.current_cam != 0:
                    # Revert to main cam after hold time
                    if time.time() - self.last_switch > CONFIG["hold_time"]:
                        self.current_cam = 0
                        self.start_stream()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            if self.ffmpeg:
                self.ffmpeg.terminate()

if __name__ == "__main__":
    switcher = Switcher1080p()
    switcher.start_stream()
    switcher.run()
