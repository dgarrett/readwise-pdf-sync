#!/usr/bin/env python3

# Testing online editor

import requests
import re
import sys
import time
from secrets import Cookie
import os.path, time

# TODO shell out to exiftool to add title based on filename if PDF has no title
# TODO shell out to qpdf to remove PDF restrictions if --is-encrypted returns 0 and --requires-password returns 3 (or as for password if it returns 0?)

start_time = int(time.time() * 1000)

pdf_page_url = 'https://readwise.io/import/pdf/'
upload_api_url = 'https://readwise.io/api/upload_misc_file'
result_api_url = 'https://readwise.io/api/sync_status'

headers = {
    'Accept': 'application/json',
    'Cookie': Cookie,
    'Referer': 'https://readwise.io/',
}

def get_csrf():
    #
    # Get the CSRF upload middleware token
    #
    pdf_page = requests.request('GET', pdf_page_url, headers=headers)
    csrf_search = re.search(r'name="csrfmiddlewaretoken" value="(.*)"', pdf_page.text, re.IGNORECASE)

    if not csrf_search:
        print('Failed to find CSRF')
        exit(-1)

    csrf = csrf_search.group(1)
    print(csrf)
    return csrf

def upload_file(file, csrf):
    #
    # Upload PDF
    #
    payload = {'file_type': 'pdf',
            'csrfmiddlewaretoken': csrf}
    files = [
        ('file', open(file, 'rb'))
    ]
    upload_response = requests.request("POST", upload_api_url, headers=headers, data = payload, files = files)
    upload_response_json = upload_response.json()

    print(upload_response.text)

    #
    # Check upload status
    #
    params = {'syncsAfter': start_time,
            'fileID': upload_response_json['file_id']}

    status_attempts = 10
    result_response_json = None
    while not result_response_json and status_attempts:
        result_response = requests.request('GET', result_api_url, headers=headers, params=params)
        res_json = result_response.json()
        if res_json['isFinished']:
            result_response_json = res_json
        status_attempts = status_attempts - 1

    if not result_response_json:
        print('Processing book failed')
        exit(-1)

    num_books = len(result_response_json["userBooks"])
    print(f'Uploaded {num_books} book(s)')
    for book in result_response_json['userBooks']:
        print(f'Finished uploading "{book["book_data__title"]}" by "{book["book_data__author"]}"')




# TODO actual arg handling
if sys.argv[1] == "-t":
    # TODO actual path handling
    with open(sys.argv[2] + '/timestamp.txt', 'w') as f:
        print(f'start time {start_time}')
        f.write(f'{start_time}')
    exit(0)

path = sys.argv[1]
list_of_files = []

with open(sys.argv[1] + '/timestamp.txt', 'r') as f:
    contents = f.read()
    print(f'contents {contents}')
    start_time = int(contents)
    print(f'start time {start_time}')

for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".pdf"):
            list_of_files.append(os.path.join(root,file))

csrf = get_csrf()

for path in list_of_files:
    print(path)
    mod_time = int(os.path.getmtime(path) * 1000)
    create_time = int(os.path.getctime(path) * 1000)
    print(f'raw modified: {mod_time}')
    print(f'raw create: {create_time}')

    if mod_time > start_time:
        upload_file(path, csrf)

