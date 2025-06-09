from flask import Flask, render_template, request
import yt_dlp as youtube_dl
from pydub import AudioSegment
from speechbrain.pretrained import EncoderClassifier
import os
import uuid

app = Flask(__name__)

# Load the classifier once
classifier = EncoderClassifier.from_hparams(
    source="Jzuluaga/accent-id-commonaccent_ecapa",
    savedir="pretrained_models/accent-id-commonaccent_ecapa"
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('video_url', '').strip()
        uploaded_file = request.files.get('audio_file')
        
        # Unique filename to avoid conflicts
        audio_basename = f"audio_{uuid.uuid4()}"
        audio_mp3 = f"{audio_basename}.mp3"
        audio_mp4 = f"{audio_basename}.mp4"
        audio_wav = f"{audio_basename}.wav"
        
        try:
            if uploaded_file and uploaded_file.filename:
                # Handle file upload (MP3 or MP4)
                ext = uploaded_file.filename.split('.')[-1].lower()
                if ext == 'mp3':
                    uploaded_file.save(audio_mp3)
                elif ext == 'mp4':
                    uploaded_file.save(audio_mp4)
                    # Extract audio from MP4 using pydub (video file)
                    from moviepy.editor import VideoFileClip
                    video = VideoFileClip(audio_mp4)
                    video.audio.write_audiofile(audio_mp3)
                    video.close()
                else:
                    return render_template('index.html', error='Unsupported file type. Please upload an MP3 or MP4 file.')
            elif video_url:
                # Handle URL input (YouTube, Loom, direct MP3/MP4, or fallback)
                if any(domain in video_url for domain in ['youtube.com', 'youtu.be', 'loom.com']):
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': audio_basename,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                elif video_url.endswith('.mp3'):
                    import requests
                    r = requests.get(video_url, stream=True)
                    with open(audio_mp3, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                elif video_url.endswith('.mp4'):
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': audio_basename,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                else:
                    try:
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'outtmpl': audio_basename,
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                        }
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([video_url])
                    except Exception:
                        return render_template('index.html', error='Unsupported URL or failed to download audio. Please provide a valid video or audio link.')
            else:
                return render_template('index.html', error='Please provide a URL or upload a file.')

            # Find the MP3 file to convert
            mp3_file = audio_mp3 if os.path.exists(audio_mp3) else f"{audio_basename}.mp3"
            # STEP 2: Convert MP3 to WAV
            audio = AudioSegment.from_file(mp3_file)
            audio.export(audio_wav, format='wav')
            
            # STEP 3: Classify Accent
            out_prob, score, index, text_lab = classifier.classify_file(audio_wav)
            accent = text_lab
            # Map accent code to country name and flag
            accent_map = {
                'US': {'name': 'United States', 'flag': '🇺🇸'},
                'UK': {'name': 'United Kingdom', 'flag': '🇬🇧'},
                'IN': {'name': 'India', 'flag': '🇮🇳'},
                'AU': {'name': 'Australia', 'flag': '🇦🇺'},
                'ZA': {'name': 'South Africa', 'flag': '🇿🇦'},
                'CA': {'name': 'Canada', 'flag': '🇨🇦'},
                'IE': {'name': 'Ireland', 'flag': '🇮🇪'},
                'NZ': {'name': 'New Zealand', 'flag': '🇳🇿'},
                # Add more as needed
            }
            accent_code = accent[0] if isinstance(accent, list) else accent
            accent_info = accent_map.get(accent_code, {'name': accent_code, 'flag': ''})
            confidence = round(float(score.max() * 100), 2)
            
            # Clean up temporary files (remove uploaded audio/video files from directory)
            for f in [audio_mp3, audio_mp4, audio_wav]:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except Exception:
                    pass  # Ignore errors if file is already removed
            return render_template('result.html', accent=accent_info['name'], flag=accent_info['flag'], confidence=confidence)
        except Exception as e:
            return render_template('index.html', error=f'Error processing: {str(e)}')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
