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
            # Direct API connection to retrieve video streams including HD/Watermark-free
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15'}
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    res_json = json.loads(response.read().decode())
                    v_data = res_json.get('data', {})
                    
                    hd_link = v_data.get('hdplay') or v_data.get('play')
                    std_link = v_data.get('play')
                    audio_link = v_data.get('music')
                    
                    if hd_link:
                        formats_list.append({'label': 'Download True HD (No Watermark)', 'url': hd_link})
                    if std_link and std_link != hd_link:
                        formats_list.append({'label': 'Download Standard Quality', 'url': std_link})
                    if audio_link:
                        formats_list.append({'label': 'Download Audio (MP3)', 'url': audio_link})
            except Exception as e:
                pass

            # Fallback API if primary fails
            if not formats_list:
                try:
                    backup_api = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
                    req_bk = urllib.request.Request(backup_api, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_bk) as resp_bk:
                        bk_data = json.loads(resp_bk.read().decode())
                        dl_url = bk_data.get('hd') or bk_data.get('download_url') or bk_data.get('result')
                        if dl_url:
                            formats_list.append({'label': 'Download True HD (No Watermark)', 'url': dl_url})
                except:
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
            return jsonify({'error': 'Could not extract video links. Please check the URL.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Server error processing link.'}), 500
