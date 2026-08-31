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
            if 'vt.tiktok.com' in url or 'vm.tiktok.com' in url:
                try:
                    req_s = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)'})
                    with urllib.request.urlopen(req_s, timeout=5) as resp_s:
                        url = resp_s.url
                except:
                    pass

            # Using TikWM with full mobile client emulation headers to prevent blocking
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
            req = urllib.request.Request(
                api_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://tikwm.com/'
                }
            )
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_json = json.loads(response.read().decode())
                    v_data = res_json.get('data', {})
                    
                    hd_link = v_data.get('hdplay')
                    play_link = v_data.get('play')
                    audio_link = v_data.get('music')
                    
                    if hd_link:
                        formats_list.append({'label': 'Download True HD (100% Original)', 'url': hd_link})
                    elif play_link:
                        # Fallback if HD is restricted for this specific link
                        formats_list.append({'label': 'Download Video (Standard)', 'url': play_link})
                        
                    if audio_link:
                        formats_list.append({'label': 'Download Audio (MP3)', 'url': audio_link})
            except Exception as e:
                pass

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
            return jsonify({'error': 'Could not fetch video links. Please try another link.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Server error processing link.'}), 500
