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
            # Primary: Use Cobalt public instance API which extracts full original raw HD streams
            try:
                cobalt_payload = json.dumps({"url": url, "vQuality": "max"}).encode('utf-8')
                req_cobalt = urllib.request.Request(
                    "https://co.wuk.sh/api/json",
                    data=cobalt_payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)'
                    }
                )
                with urllib.request.urlopen(req_cobalt) as resp_c:
                    c_data = json.loads(resp_c.read().decode())
                    if c_data.get('status') == 'stream' or c_data.get('url'):
                        dl_url = c_data.get('url')
                        formats_list.append({'label': 'Download True HD (130MB+ Original)', 'url': dl_url})
                    elif c_data.get('status') == 'picker':
                        for item in c_data.get('picker', []):
                            if item.get('type') == 'video':
                                formats_list.append({'label': 'Download True HD (Original)', 'url': item.get('url')})
            except:
                pass

            # Fallback to TikWM HD if Cobalt fails
            if not formats_list:
                try:
                    api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        res_json = json.loads(response.read().decode())
                        v_data = res_json.get('data', {})
                        hd_link = v_data.get('hdplay') or v_data.get('play')
                        if hd_link:
                            formats_list.append({'label': 'Download True HD (No Watermark)', 'url': hd_link})
                            if v_data.get('music'):
                                formats_list.append({'label': 'Download Audio (MP3)', 'url': v_data.get('music')})
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
            return jsonify({'error': 'Could not extract high quality video. Please try again.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Server error processing link.'}), 500
