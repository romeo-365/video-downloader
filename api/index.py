from flask import Flask, request, jsonify
import urllib.request
import urllib.parse
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
            try:
                # Step 1: Hit ssstik.io to extract session token ('tt')
                req_session = urllib.request.Request(
                    "https://ssstik.io/en",
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                )
                
                with urllib.request.urlopen(req_session, timeout=10) as resp:
                    html_content = resp.read().decode('utf-8')
                    # Find the token variable 'tt'
                    tt_match = re.findall(r"tt:\'([\w\d]+)\'", html_content)
                    
                    if tt_match:
                        tt_token = tt_match[0]
                        
                        # Step 2: Post the TikTok URL along with the extracted token to SSSTik backend endpoint
                        form_data = urllib.parse.urlencode({
                            'id': url,
                            'locale': 'en',
                            'tt': tt_token
                        }).encode('utf-8')
                        
                        req_abc = urllib.request.Request(
                            "https://ssstik.io/abc?url=dl",
                            data=form_data,
                            headers={
                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'HX-Request': 'true',
                                'HX-Current-URL': 'https://ssstik.io/en',
                                'Origin': 'https://ssstik.io',
                                'Referer': 'https://ssstik.io/en'
                            }
                        )
                        
                        with urllib.request.urlopen(req_abc, timeout=10) as abc_resp:
                            result_html = abc_resp.read().decode('utf-8')
                            
                            # Step 3: Extract download links from the returned HTML snippet
                            links = re.findall(r'href="(https://[^"]+)"', result_html)
                            for link in links:
                                if 'download' in link or '.mp4' in link or 'ssstik' in link:
                                    if 'dl.ssstik.io' in link or 'tikwm' in link or 'download' in link:
                                        formats_list.append({
                                            'label': 'Download True HD (SSSTik Engine)',
                                            'url': link
                                        })
                                        break
            except Exception as e:
                pass

            # Fallback to TikWM if SSSTik scraper gets rate-limited
            if not formats_list:
                try:
                    fallback_url = f"https://tikwm.com/api/?url={urllib.parse.quote(url)}&hd=1"
                    req_alt = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
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
            return jsonify({'error': 'Could not extract HD stream. Try another link.'}), 400

        # Remove duplicate URLs if any
        seen = set()
        unique_formats = []
        for fmt in formats_list:
            if fmt['url'] not in seen:
                seen.add(fmt['url'])
                unique_formats.append(fmt)

        return jsonify({'formats': unique_formats})

    except Exception as e:
        return jsonify({'error': 'Server error processing link.'}), 500
