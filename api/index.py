from flask import Flask, request, jsonify
import urllib.request
import json

app = Flask(__name__)

@app.route('/api/get-links', methods=['POST'])
def get_links():
    data = request.get_json()
    url = data.get('url')
    platform = data.get('platform')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Using a reliable public API endpoint that extracts direct video streams
        api_url = f"https://tikwm.com/api/?url={url}" if platform == 'tiktok' else f"https://apis.davidcyriltech.my.id/download?url={url}"
        
        req = urllib.request.Request(
            api_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            
            formats_list = []
            
            if platform == 'tiktok':
                # TikWM api structure for direct mp4 video
                video_dl = res_data.get('data', {}).get('play', '')
                music_dl = res_data.get('data', {}).get('music', '')
                
                if video_dl:
                    formats_list.append({'label': 'Download No Watermark (HD)', 'url': video_dl})
                if music_dl:
                    formats_list.append({'label': 'Download Audio (MP3)', 'url': music_dl})
            else:
                download_url = res_data.get('download_url', res_data.get('result', url))
                formats_list.append({'label': 'Download Video File', 'url': download_url})

            if not formats_list:
                formats_list.append({'label': 'Download Media', 'url': url})

            return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
