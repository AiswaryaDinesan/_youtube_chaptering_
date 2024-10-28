import re
import csv
import pandas as pd
from flask import Flask, render_template, request, send_file
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF

app = Flask(__name__)

API_KEY = 'AIzaSyDd3B4VNpRROwtEvcuopDTsvN9rfc5bljE'

def get_video_id(url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id_match.group(1) if video_id_match else None

def get_video_title(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    return response['items'][0]['snippet']['title'] if response['items'] else 'Unknown Title'

def get_video_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def save_to_csv(title, transcript, filename):
    transcript_data = [{'start': entry['start'], 'text': entry['text']} for entry in transcript]
    df = pd.DataFrame(transcript_data)
    df.to_csv(filename, index=False)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title:', title])

def clean_text(text):
    # Remove common filler words
    filler_words = ['uh', 'um', 'like', 'you know', 'right', 'll', 'want', 'just']
    words = text.split()
    cleaned_words = [word for word in words if word.lower() not in filler_words]
    return ' '.join(cleaned_words)

def create_chapters(transcript_df, interval=600):
    # Convert 'start' to numeric and drop NaN values
    transcript_df['start'] = pd.to_numeric(transcript_df['start'], errors='coerce')
    transcript_df = transcript_df.dropna(subset=['start'])

    # Create time-based chapters every `interval` seconds (default: 10 minutes)
    max_time = transcript_df['start'].max()
    chapter_starts = list(range(0, int(max_time), interval))
    
    chapter_points = []
    chapter_names = []

    for i, start_time in enumerate(chapter_starts):
        # Extract the text for this chapter based on the time interval
        chapter_text = transcript_df[(transcript_df['start'] >= start_time) & 
                                     (transcript_df['start'] < start_time + interval)]['text'].str.cat(sep=' ')
        
        # Clean the text by removing filler words
        chapter_text = clean_text(chapter_text)

        # Generate a title based on important words in the chapter text
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5)
        if chapter_text.strip():
            tfidf_matrix = vectorizer.fit_transform([chapter_text])
            feature_names = vectorizer.get_feature_names_out()
            chapter_name = " ".join(feature_names)
        else:
            chapter_name = "Topic Not Available"  # Fallback if no content

        # Convert the start time to H:M:S format
        chapter_time = pd.to_datetime(start_time, unit='s').strftime('%H:%M:%S')
        chapter_points.append(chapter_time)
        chapter_names.append(f"Chapter {i + 1}: {chapter_name}")

    return chapter_points, chapter_names


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['youtube_url']
        video_id = get_video_id(url)

        if not video_id:
            return "Invalid YouTube URL."

        title = get_video_title(video_id)
        transcript = get_video_transcript(video_id)

        if not transcript:
            return "No transcript available for this video."

        filename = f"{video_id}_transcript.csv"
        save_to_csv(title, transcript, filename)

        transcript_df = pd.read_csv(filename)
        chapter_points, chapter_names = create_chapters(transcript_df)

        return render_template('after.html', chapter_points=chapter_points, chapter_names=chapter_names, video_id=video_id)

    return render_template('index.html')

@app.route('/download/<video_id>')
def download_file(video_id):
    filename = f"{video_id}_transcript.csv"
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 