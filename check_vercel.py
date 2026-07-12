import urllib.request
import re

req = urllib.request.Request('https://pilot-ai-six.vercel.app/analyse')
html = urllib.request.urlopen(req).read().decode('utf-8')

js_files = re.findall(r'/_next/static/chunks/[^\"]+\.js', html)
for js in js_files:
    js_url = 'https://pilot-ai-six.vercel.app' + js
    try:
        js_content = urllib.request.urlopen(js_url).read().decode('utf-8')
        if 'pilot-ai-production' in js_content:
            idx = js_content.find('pilot-ai-production')
            print('URL found in JS:', js_content[idx-20:idx+60])
    except Exception as e:
        pass
