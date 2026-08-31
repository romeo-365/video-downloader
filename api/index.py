from flask import Flask, request, jsonify
import urllib.request
import json
import urllib.parse

app = Flask(__name__)

@app.route('/api/get-links', methods=['POST'])
def get_links():
    data = request.get_json()
    url = data.get('url')
    platform = data.get('platform')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        formats_list = []
        
        if platform == 'tiktok':
            # TikTok extraction via TikWM API
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                vid_url = res_data.get('data', {}).get('play')
                music_url = res_data.get('data', {}).get('music')
                if vid_url:
                    formats_list.append({'label': 'Download No Watermark (HD)', 'url': vid_url})
                if music_url:
                    formats_list.append({'label': 'Download Audio (MP3)', 'url': music_url})

        elif platform == 'youtube':
            # YouTube extraction via Cobalt / public robust proxy or API
            yt_api = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
            req = urllib.request.Request(yt_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                download_url = res_data.get('download_url') or res_data.get('result') or res_data.get('video', {}).get('url')
                if download_url:
                    formats_list.append({'label': 'Download YouTube Video (HD)', 'url': download_url})
                else:
                    # Fallback generic stream search if API fails
                    formats_list.append({'label': 'Download Video Stream', 'url': url})

        elif platform == 'instagram':
            insta_api = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
            req = urllib.request.Request(insta_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                download_url = res_data.get('download_url') or res_data.get('result')
                if download_url:
                    formats_list.append({'label': 'Download Instagram Video', 'url': download_url})

        if not formats_list:
            return jsonify({'error': 'Could not extract direct links for this media. Please try another link.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Failed to process link. Please check the URL.'}), 500
