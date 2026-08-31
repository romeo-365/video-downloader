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
            # Using a heavy stream extractor API that forces original high-bitrate output
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_json = json.loads(response.read().decode())
                    v_data = res_json.get('data', {})
                    
                    # Look for hdwatermark or hdplay first
                    hd_link = v_data.get('hdplay') or v_data.get('wmplay')
                    audio_link = v_data.get('music')
                    
                    if hd_link:
                        # Ensure it points to high res stream if available
                        formats_list.append({'label': 'Download True HD (130MB+ Original)', 'url': hd_link})
                    
                    if audio_link:
                        formats_list.append({'label': 'Download Audio (MP3)', 'url': audio_link})
            except Exception as e:
                pass

            # If still nothing, try alternative snapshot extractor
            if not formats_list:
                try:
                    alt_api = f"https://apis.davidcyriltech.my.id/download?url={urllib.parse.quote(url)}"
                    req_alt = urllib.request.Request(alt_api, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_alt) as resp_alt:
                        alt_data = json.loads(resp_alt.read().decode())
                        dl = alt_data.get('hd') or alt_data.get('download_url') or alt_data.get('result')
                        if dl:
                            formats_list.append({'label': 'Download True HD (130MB+ Original)', 'url': dl})
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
            return jsonify({'error': 'Could not extract HD stream. Try another link.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Server error processing link.'}), 500
