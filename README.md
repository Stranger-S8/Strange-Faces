# Strange Faces

A desktop face-recognition attendance and administration system.

## Overview

Strange Faces is a CustomTkinter application for registering student faces, training recognition data, capturing attendance, and generating reports. It includes database helpers, image upload logic, OpenCV detection assets, and local training/dataset folders.

## Key Features

- Admin login workflow
- Student registration with image upload
- Face encoding and training assets
- Attendance capture and PDF report output
- MySQL-backed data helpers
- Google Drive upload helper
- Local image assets for the desktop UI

## Tech Stack

- Python
- CustomTkinter
- OpenCV
- Pillow
- MySQL connector
- FPDF

## Project Structure

```text
.
|-- main.py                         # Desktop application
|-- FaceEncoder.py                  # Face encoding workflow
|-- Detection.py                    # Detection logic
|-- database.py                     # Database access helpers
|-- drive.py                        # Drive upload helper
|-- haarcascade_frontalface_default.xml
|-- data/                           # UI assets and local data
|-- dataset/                        # Local training images
|-- Training/                       # Training outputs
`-- output/                         # Generated attendance reports
```

## Getting Started

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## GitHub Notes

Do not publish real student photos, attendance PDFs, service account files, or generated encodings. Use sample/anonymized data only.
