# ERNESTYT Segment Downloader

A lightweight, locally hosted YouTube segment downloader with a minimal red-and-white Ernest-branded interface. Paste a video URL, choose the start and end timestamps, and save the requested clip to your Downloads folder.


> **Important:** Use this project only for videos you own, have permission to download, or that are otherwise permitted by applicable law and YouTube's terms. This project is not affiliated with YouTube or Google.

## Features

- **Segment selection:** Enter a start and end time in seconds, `MM:SS`, or `HH:MM:SS`.
- **Best available quality:** Selects the best available video and audio streams; no fixed 1080p cap (higher resolutions may be available depending on the source).
- **Local web interface:** Runs on `127.0.0.1` and opens in your default browser.
- **Output folder shortcut:** Open the output folder from the interface after a completed download.
- **Download another clip:** Reset the interface to process another video.
- **Custom background:** Select a local image to customize the page background.
- **Ernest identity:** Red-and-white interface, E favicon, and “Powered by Ernest”.
- **Duration check:** Uses `ffprobe` to verify the resulting clip duration when available.

## Preview

_Add a screenshot of the application here after taking one, for example:_

```md
![ERNESTYT Segment Downloader screenshot](assets/screenshot.png)
```

## Requirements

- Windows 10 or Windows 11
- Python 3.10+ recommended
- FFmpeg (including `ffmpeg` and `ffprobe` available in `PATH`)
- Internet connection while downloading and installing Python dependencies


## Installation & usage (Windows)

1. Download this repository (GitHub **Code → Download ZIP**) and extract it, or clone it with Git.
2. Install Python from [python.org](https://www.python.org/downloads/). If using the installer, enable **Add Python to PATH**.
3. Install FFmpeg and ensure both `ffmpeg.exe` and `ffprobe.exe` are available in `PATH`. Reopen Command Prompt after updating PATH.
4. Open the extracted project folder.
5. Double-click `RUN_LOCAL.cmd`.
6. On first launch, the script creates a virtual environment and installs the Python packages listed in `requirements.txt`. Allow a moment for this setup to finish.
7. The local web page should open automatically at `http://127.0.0.1:5050`.
8. Paste a YouTube URL, set **Start time** and **End time**, and click **Download selected segment**.
9. After completion, use **Show video in folder** to open the output location. Choose **Download another video** to reset the form.

### Timestamp examples

| Input | Meaning |
|---|---|
| `75` | 75 seconds |
| `01:15` | 1 minute 15 seconds |
| `00:01:15` | 1 minute 15 seconds |

The end time must be greater than the start time. The selected range should be within the video's duration.

## Output location

Clips are saved in:

```text
%USERPROFILE%\Downloads\Download
```

## How quality selection works

The downloader asks `yt-dlp` for the best available video and audio streams. If a source offers 1440p, 4K, or another resolution above 1080p, it may choose that higher quality. Actual available quality depends on the source video and stream formats.

## Troubleshooting

- **FFmpeg/FFprobe not detected:** Confirm they are installed and on PATH, then close and reopen the terminal and rerun the launcher.
- **Browser did not open:** Manually open `http://127.0.0.1:5050` while the launcher is running.
- **Port is already in use:** Close any other instance of this app or check which process is using port `5050`.
- **Download errors:** Update dependencies by rerunning `RUN_LOCAL.cmd`; `yt-dlp` changes frequently, so current versions may be required.
- **Unexpected duration:** Check the input timestamps and source availability. The app's duration verification is a safeguard, not a guarantee that every source behaves identically.

## Project structure

```text
ERNESTYT_SegmentDownloader/
├── app.py
├── requirements.txt
├── RUN_LOCAL.cmd
├── README.md
├── LICENSE
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── favicon.svg
    ├── favicon.png
    └── favicon.ico
```

## Tech stack

- Python
- Flask
- yt-dlp
- FFmpeg / FFprobe
- HTML, CSS, JavaScript

## License

Distributed under the MIT License. See `LICENSE` for details.


---

**Made by Ernest · ERNESTYT**
