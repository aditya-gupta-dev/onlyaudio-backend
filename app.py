from flask import Flask, request, Response, jsonify
from requests import get
import pytube
import os
from flask_cors import CORS

key = os.getenv('key')
url = 'https://www.googleapis.com/youtube/v3/videos'

app = Flask(__name__)
CORS(app)


def get_audio_data(id):
  yt = pytube.YouTube(f'https://youtu.be/{id}')

  formats = yt.streaming_data['adaptiveFormats']

  content_length_with_urls = []

  for format in formats:
    if 'audio' in format['mimeType']:
      content_length_with_urls.append({
        'contentLength': format["contentLength"],
        'url': format["url"]
      })
  return content_length_with_urls


@app.route('/')
def index():
  return {"message": "index page"}


@app.route("/video")
def vid():
  query = request.headers.get('q')
  maxResults = request.headers.get('maxResults')

  if maxResults == None:
    maxResults = 5

  if query == None:

    message = {"message": "query not provided"}

    return Response(status=400, response=jsonify(message))
  else:
    base_url = 'https://www.googleapis.com/youtube/v3/search'

    params = {
      'part': 'snippet',
      'q': query,
      'type': 'video',
      'maxResults': maxResults,
      'key': key
    }
    vid_info = []
    items = get(base_url, params=params).json()["items"]

    for item in items:
      vid_info.append({
        'id':
        item['id']['videoId'],
        'thumbnailUrl':
        item['snippet']['thumbnails']['default']['url'],
        'title':
        item['snippet']['title']
      })

    return vid_info


@app.route('/audio')
def audio():
  id = request.headers.get('id')
  if id is None:
    return {"message": "id of the youtube video not provided"}
  else:
    data = get_audio_data(id)
    lowest = min(range(len(data)), key=lambda i: data[i]['contentLength'])
    return data[lowest]


app.run(host='0.0.0.0', port=81)
