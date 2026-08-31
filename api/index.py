from flask import Flask, request, jsonify
import urllib.request
import json
import urllib.parse
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
            # Method 1: Try TikWM API first
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)'})
            
            hd_url = None
            normal_url = None
            music_url = None

            try:
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode())
                    video_data = res_data.get('data', {})
                    hd_url = video_data.get('hdplay') or video_data.get('play')
                    normal_url = video_data.get('play')
                    music_url = video_data.get('music')
            except:
                pass

            # Method 2: If HD not found via TikWM, try alternative endpoint
            if not hd_url or hd_url == normal_url:
                try:
                    alt_api = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
                    req_alt = urllib.request.Request(alt_api, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_alt) as resp_alt:
                        alt_data = json.loads(resp_alt.read().decode())
                        alt_hd = alt_data.get('hd') or alt_data.get('download_url') or alt_data.get('result')
                        if alt_hd:
                            hd_url = alt_hd
                except:
                    pass

            # Populate formats ensuring HD is top priority
            if hd_url:
                formats_list.append({'label': 'Download HD No Watermark (Highest)', 'url': hd_url})
            if normal_url and normal_url != hd_url:
                formats_list.append({'label': 'Download Standard Quality', 'url': normal_url})
            if music_url:
                formats_list.append({'label': 'Download Audio (MP3)', 'url': music_url})

        elif platform == 'youtube':
            yt_api = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
            req = urllib.request.Request(yt_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                download_url = res_data.get('download_url') or res_data.get('result') or res_data.get('video', {}).get('url')
                if download_url:
                    formats_list.append({'label': 'Download YouTube Video (HD)', 'url': download_url})

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
