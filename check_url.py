import urllib.request
import re

html = urllib.request.urlopen('https://pilot-ai-six.vercel.app/analyse').read().decode('utf-8')
js_files = re.findall(r'src="(/_next/static/chunks/app/analyse/[^"]+\.js)"', html)
for js_file in js_files:
    js_url = 'https://pilot-ai-six.vercel.app' + js_file
    js_code = urllib.request.urlopen(js_url).read().decode('utf-8')
    print("Found 'api/health'?:", 'health' in js_code)
    # search for the definition of API_BASE or BASE_URL
    # We can just look for 'http' strings.
    print("URLs in JS:")
    urls = re.findall(r'"(https?://[^"]+)"', js_code)
    for u in urls:
        print(u)
