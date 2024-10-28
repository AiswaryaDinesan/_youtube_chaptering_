# YouTube Transcript and Chapter Generator

This project is a web application built with Flask that allows users to input a YouTube video URL and generates a transcript along with chapters based on the video's content. It utilizes the YouTube Data API and the YouTube Transcript API to fetch video details and transcripts, respectively.

## Features

- **Fetch Video Title**: Retrieves the title of the YouTube video.
- **Transcript Generation**: Extracts the transcript of the video, if available.
- **Chapter Creation**: Divides the transcript into chapters based on time intervals and generates chapter titles using important keywords.
- **CSV Export**: Saves the video transcript and details to a CSV file for easy access.
- **Web Interface**: A user-friendly web interface for submitting YouTube URLs and viewing results.

## Technologies Used

- **Flask**: Web framework for Python.
- **YouTube Data API**: For retrieving video details.
- **YouTube Transcript API**: For fetching transcripts.
- **Pandas**: For data manipulation and CSV handling.
- **Scikit-learn**: For natural language processing and text analysis.
- **HTML/CSS**: For frontend development.

## Requirements

To run this project, you need the following:

- Python 3.x
- Flask
- google-api-python-client
- youtube-transcript-api
- pandas
- scikit-learn

You can install the required packages using pip:

```bash
pip install Flask google-api-python-client youtube-transcript-api pandas scikit-learn
