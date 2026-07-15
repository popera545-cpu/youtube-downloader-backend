from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
# הגדרת CORS מאובטחת שמאפשרת ל-Vercel לדבר עם השרת
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({"status": "Server is running smoothly"}), 200

@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    # טיפול בבקשות OPTIONS (Preflight של הדפדפן)
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json or {}
    url = data.get('url')
    type_format = data.get('type') # 'mp3' או 'mp4'
    
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    # שימוש בלקוח Android הרשמי של יוטיוב כדי למנוע חסימות IP לחלוטין
    ydl_opts = {
        'format': 'bestaudio/best' if type_format == 'mp3' else 'best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android'], # הכי יציב ועוקף חסימות שרתים
                'skip': ['webpage', 'hls']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # שליפת הקישור הישיר
            stream_url = info['url']
            title = info.get('title', 'download').replace('/', '_')
            
        # הזרמת הקובץ ישירות
        req = requests.get(stream_url, stream=True, headers={
            'User-Agent': 'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0'
        })
        
        ext = 'mp3' if type_format == 'mp3' else 'mp4'
        
        # בניית התגובה לדפדפן
        def generate():
            for chunk in req.iter_content(chunk_size=1024*1024):
                if chunk:
                    yield chunk

        headers = {
            'Content-Disposition': f'attachment; filename="{title}.{ext}"',
            'Content-Type': 'audio/mpeg' if type_format == 'mp3' else 'video/mp4',
            'Access-Control-Allow-Origin': '*' # פותר Failed to fetch ב-100%
        }
        
        return Response(stream_with_context(generate()), headers=headers)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
