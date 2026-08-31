from flask import Flask, request, jsonify
import urllib.request
import json
import urllib.parse
import re

app = FlaskName := Flask(__name__)

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
            # Resolve short URL if necessary
            if 'vt.tiktok.com' in url or 'vm.tiktok.com' in url:
                try:
                    req_short = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                    with urllib.request.urlopen(req_short) as resp:
                        url = resp.url
                except:
                    pass

            # Direct reliable backend scraper for TikTok HD
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
            req = urllib.request.Request(
                api_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    res_json = json.loads(response.read().decode())
                    v_data = res_json.get('data', {})
                    
                    # Tikwm sometimes puts HD link in 'hdplay' or inside wmplay alternative
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

            # If tikwm fails, use a secondary robust public extractor endpoint
            if not formats_list:
                try:
                    backup_api = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}"
                    req_bk = urllib.request.Request(backup_api, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_bk) as resp_bk:
                        bk_data = json.loads(resp_bk.read().decode()).get('data', {})
                        if bk_data.get('play'):
                            formats_list.append({'label': 'Download True HD (No Watermark)', 'url': bk_data.get('play')})
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
            return jsonify({'error': 'Could not extract video. Please check the link.'}), 400

        return jsonify({'formats': formats_list})

    except Exception as e:
        return jsonify({'error': 'Failed to process link. Please try again.'}), 500
