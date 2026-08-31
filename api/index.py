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
            # Cobalt engine request with extended timeout
            try:
                payload = json.dumps({
                    "url": url,
                    "vQuality": "max",
                    "dubLang": False,
                    "disableMetadata": True
                }).encode('utf-8')
                
                req = urllib.request.Request(
                    "https://co.wuk.sh/api/json",
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=15) as resp:
                    res_data = json.loads(resp.read().decode())
                    status = res_data.get('status')
                    
                    if status == 'stream':
                        formats_list.append({'label': 'Download True HD (100% Original)', 'url': res_data.get('url')})
                    elif status == 'picker':
                        for item in res_data.get('picker', []):
                            if item.get('type') == 'video':
                                formats_list.append({'label': 'Download True HD (100% Original)', 'url': item.get('url')})
                    elif status == 'redirect':
                        formats_list.append({'label': 'Download True HD (100% Original)', 'url': res_data.get('url')})
            except Exception as e:
                pass

            # Fallback to absolute direct stream if Cobalt fails
            if not formats_list:
                try:
                    alt_api = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
                    req_alt = urllib.request.Request(alt_api, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_alt, timeout=8) as resp_alt:
                        alt_json = json.loads(resp_alt.read().decode())
                        v_data = alt_json.get('data', {})
                        hd = v_data.get('hdplay') or v_data.get('play')
                        if hd:
                            formats_list.append({'label': 'Download HD Video', 'url': hd})
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
            return jsonify({'error': 'Failed to fetch HD stream. Please try a different link.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Server error processing link.'}), 500
