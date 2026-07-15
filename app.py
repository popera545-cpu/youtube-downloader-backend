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

    # הגדרות מתקדמות שגורמות לשרת להיראות כמו דפדפן רגיל של משתמש אמיתי
    ydl_opts = {
        'format': 'bestaudio/best' if type_format == 'mp3' else 'best/best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # בחירת פורמט נכון
            if type_format == 'mp3':
                stream_url = info['url']
            else:
                # מוצא את הקישור לוידאו המשולב עם אודיו הכי טוב
                formats = [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
                stream_url = formats[-1]['url'] if formats else info['url']
                
            title = info.get('title', 'download').replace('/', '_')
            
        # הזרמת הקובץ
        req = requests.get(stream_url, stream=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        ext = 'mp3' if type_format == 'mp3' else 'mp4'
        
        headers = {
            'Content-Disposition': f'attachment; filename="{title}.{ext}"',
            'Content-Type': 'audio/mpeg' if type_format == 'mp3' else 'video/mp4'
        }
        
        return Response(stream_with_context(req.iter_content(chunk_size=1024*1024)), headers=headers)
    except Exception as e:
        print(f"Error occurred: {str(e)}") # יודפס בלוגים של רנדר למעקב
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(port=5000)
