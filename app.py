from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.json or {}
    url = data.get('url')
    type_format = data.get('type') # 'mp3' או 'mp4'

    if not url:
        return {"error": "Missing URL"}, 400

    ydl_opts = {
        'format': 'bestaudio/best' if type_format == 'mp3' else 'bestvideo+bestaudio/best',
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info['url'] if type_format == 'mp3' else info['formats'][-1]['url']
            title = info.get('title', 'download').replace('/', '_')

        req = requests.get(stream_url, stream=True)
        ext = 'mp3' if type_format == 'mp3' else 'mp4'

        headers = {
            'Content-Disposition': f'attachment; filename="{title}.{ext}"',
            'Content-Type': 'audio/mpeg' if type_format == 'mp3' else 'video/mp4'
        }

        return Response(stream_with_context(req.iter_content(chunk_size=1024*1024)), headers=headers)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(port=5000)
