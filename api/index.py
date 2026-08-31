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

    # yt-dlp options configured to bypass blocks and 403 errors
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'tiktok': {'webpage_download': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats_list = []
            
            # Extract direct stream URL
            video_url = info.get('url')
            if not video_url and 'entries' in info:
                # Handle playlists or multi-item posts
                video_url = info['entries'][0].get('url')

            if not video_url:
                return jsonify({'error': 'Could not extract video stream. Try another link.'}), 400

            if platform == 'tiktok':
                formats_list = [
                    {'label': 'Download No Watermark (HD)', 'url': video_url},
                    {'label': 'Download MP3 Audio', 'url': info.get('acodec') and video_url or video_url}
                ]
            elif platform == 'instagram':
                formats_list = [
                    {'label': 'Download HD Video', 'url': video_url}
                ]
            else: # YouTube
                formats_list = [
                    {'label': 'Download Video (HD)', 'url': video_url}
                ]

            return jsonify({'formats': formats_list})

    except Exception as e:
        # Return friendly error message without crashing
        err_msg = str(e)
        if '403' in err_msg:
            err_msg = "Platform blocked the request (403). Please try again or use another link."
        return jsonify({'error': err_msg}), 500
