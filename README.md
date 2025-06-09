# Accent Detection Flask App

This web application detects the accent from a YouTube/Loom video link or an uploaded MP3/MP4 file using deep learning models.

## Features
- Accepts YouTube and Loom video links for accent detection.
- Allows uploading MP3 or MP4 files from your local machine (audio or video).
- Converts all audio to WAV format for processing.
- Uses a pre-trained SpeechBrain ECAPA model for accent classification.
- Displays the detected accent with a country flag, full country name, and confidence score.
- Cleans up all temporary files after processing.

## Libraries Used
- **Flask**: Web framework for building the API and web interface.
- **yt-dlp**: Downloads and extracts audio from YouTube, Loom, and other video links.
- **pydub**: Handles audio file conversion (e.g., MP3 to WAV).
- **speechbrain**: Provides the pre-trained ECAPA model for accent classification.
- **torch**: Backend for running the SpeechBrain deep learning model.
- **moviepy**: Extracts audio from uploaded MP4 video files.
- **requests**: (Used internally) Downloads direct MP3 files from URLs.

## Setup Instructions

1. **Clone the repository or copy the files to your machine.**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the pre-trained model:**
   The first time you run the app, SpeechBrain will automatically download the ECAPA accent model to `pretrained_models/accent-id-commonaccent_ecapa`.

4. **Run the Flask app:**
   ```bash
   python app.py
   ```
   The app will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Usage

- **Option 1: Provide a YouTube or Loom video link**
  - Paste the link in the input field and submit.
- **Option 2: Upload an MP3 or MP4 file**
  - Click the upload button, select your file, and submit.

The app will process the audio, classify the accent, and display the result with a flag, country name, and confidence score.

## Notes
- Only public YouTube/Loom links and standard MP3/MP4 files are supported.
- All temporary files are deleted after each request for security and cleanliness.
- For best results, use clear audio with minimal background noise.

## License
This project is for educational and research purposes.
