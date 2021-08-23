#!/usr/bin/env python3

import requests
import re
import sys
from secrets import Cookie

pdf_page_url = 'https://readwise.io/import/pdf/'
api_url = "https://readwise.io/api/upload_misc_file"

headers = {
    'Accept': 'application/json',
    'Cookie': Cookie,
    'Referer': 'https://readwise.io/import/pdf/',
    'Content-Type': 'multipart/form-data; boundary=--------------------------005826398629307083381548'
}

pdf_page = requests.request('GET', pdf_page_url, headers=headers)
csrf_search = re.search(r'name="csrfmiddlewaretoken" value="(.*)"', pdf_page.text, re.IGNORECASE)

if not csrf_search:
    print('Failed to find CSRF')
    exit(-1)

csrf = csrf_search.group(1)
print(csrf)

payload = {'file_type': 'pdf',
           'csrfmiddlewaretoken': csrf}
files = [
    ('file', open(sys.argv[1], 'rb'))
]
response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
