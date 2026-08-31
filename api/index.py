from flask import Flask, request, jsonify
import urllib.request
import json
import re

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
            # Resolve short URLs if needed (e.g. vt.tiktok.com)
            if 'vt.tiktok.com' in url or 'vm.tiktok.com' in url:
                req_short = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    with urllib.request.urlopen(req_short) as resp:
                        url = resp.url
                except:
                    pass

            # Fetch video ID using regex
            video_id_match = re.search(r'/video/(\d+)', url)
            if not video_id_match:
                # Try fallback API method for tiktok
                api_fallback = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}"
                req_fb = urllib.request.Request(api_fallback, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_fb) as response:
                    res_data = json.loads(response.read().decode())
                    vid_url = res_data.get('data', {}).get('play')
                    music_url = res_data.get('data', {}).get('music')
                    if vid_url:
                        formats_list.append({'label': 'Download No Watermark (HD)', 'url': vid_url})
                    if music_url:
                        formats_list.append({'label': 'Download Audio (MP3)', 'url': music_url})
            
            if not formats_list:
                # Direct TikWM query
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

        else:
            # General fallback for other platforms
            formats_list.append({'label': 'Download Media File', 'url': url})

        if not formats_list:
            return jsonify({'error': 'Could not fetch video. Please check the link.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Failed to process link. Please try again.'}), 500
