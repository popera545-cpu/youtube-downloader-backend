from flask import Flask, request, send_file
import yt_dlp
import time
import os

app = Flask(__name__)

# זה עיצוב האתר הפשוט שכולם יראו כשיכנסו ללינק שלך
HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>הורדות וידאו</title>
</head>
<body style="text-align: center; font-family: Arial; margin-top: 50px; background: #111; color: white;">
    <h1 style="color: #ff4444;">הורדת סרטונים ישירה</h1>
    <form action="/download" method="get">
        <input type="text" name="url" placeholder="הדבק לינק ליוטיוב..." style="padding: 15px; width: 80%; max-width: 400px; border-radius: 5px; border: none;">
        <br><br>
        <button type="submit" style="padding: 15px 30px; background: #ff4444; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer;">הורד עכשיו</button>
    </form>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return "חסר לינק!", 400
    
    # נותן שם ייחודי לכל קובץ כדי שאנשים לא ידרסו אחד לשני את ההורדות
    filename = f"video_{int(time.time())}.mp4"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': filename,
        'cookiefile': 'cookies.txt', # חסינות מיוטיוב
        'quiet': True
    }
    
    try:
        # הספרייה עושה את העבודה
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # שולח את הקובץ למשתמש שהוריד
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"קרתה שגיאה: {str(e)}"

if __name__ == '__main__':
    # מריץ את השרת על הפורט ש-Render דורש
    app.run(host='0.0.0.0', port=10000)
