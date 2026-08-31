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
            # Using robust multi-source API that fetches real HD links like SSSTIK
            api_url = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)'})
            
            try:
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode())
                    # Check different possible keys returned by high-quality endpoints
                    hd_url = res_data.get('hd') or res_data.get('hd_video') or res_data.get('download_url') or res_data.get('result')
                    normal_url = res_data.get('video') or res_data.get('download_url') or res_data.get('result')
                    music_url = res_data.get('audio') or res_data.get('music')

                    if hd_url:
                        formats_list.append({'label': 'Download True HD (130MB+ Original)', 'url': hd_url})
                    if normal_url and normal_url != hd_url:
                        formats_list.append({'label': 'Download Standard Quality', 'url': normal_url})
                    if music_url:
                        formats_list.append({'label': 'Download Audio (MP3)', 'url': music_url})
            except Exception as e:
                pass

            # Fallback if primary didn't catch true HD
            if not formats_list:
                fallback_api = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
                req_fb = urllib.request.Request(fallback_api, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_fb) as resp_fb:
                    fb_data = json.loads(resp_fb.read().decode()).get('data', {})
                    if fb_data.get('hdplay'):
                        formats_list.append({'label': 'Download True HD (130MB+ Original)', 'url': fb_data.get('hdplay')})
                    if fb_data.get('play'):
                        formats_list.append({'label': 'Download Standard Quality', 'url': fb_data.get('play')})

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
            return jsonify({'error': 'Could not extract high quality links. Please try again.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Failed to process link. Please check the URL.'}), 500
