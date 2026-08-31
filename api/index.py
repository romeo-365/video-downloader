from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/get-links', methods=['POST'])
def get_links():
    data = request.get_json()
    url = data.get('url')
    platform = data.get('platform')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            formats_list = []
            
            if platform == 'tiktok':
                formats_list = [
                    {'label': 'Download MP3 Audio', 'url': video_url},
                    {'label': 'Download No Watermark', 'url': video_url},
                    {'label': 'Download HD No Watermark', 'url': video_url}
                ]
            elif platform == 'instagram':
                formats_list = [
                    {'label': 'Download No Watermark', 'url': video_url},
                    {'label': 'Download HD No Watermark', 'url': video_url}
                ]
            else: # YouTube
                formats_list = [
                    {'label': 'Download in 360p', 'url': video_url},
                    {'label': 'Download in 480p', 'url': video_url},
                    {'label': 'Download in 720p (HD)', 'url': video_url},
                    {'label': 'Download in 1080p (FHD)', 'url': video_url},
                    {'label': 'Download in 2K', 'url': video_url},
                    {'label': 'Download in 4K (UHD)', 'url': video_url}
                ]

            return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
