# -*- coding: UTF-8 -*-
import os
import glob
import time
import json
import requests
import threading
from retrying import retry

# global
downloaded = 0


# analysis page (create no more than 20 threads per call)
@retry
def bs_spider_page(dir, url, type_, by, page):
    iurl = url + type_ + '/top/json?by=' + by + '&page=' + str(page)
    req = requests.get(iurl)
    res = json.loads(req.text).get('data').get('items')
    for each in res:
        id = str(each['id'])
        # analysis item of page
        threading.Thread(target=bs_spider_item, args=(dir, url, type_, by, page, id)).start()


# analysis item of page (create about 10 threads per call)
@retry
def bs_spider_item(dir, url, type_, by, page, id):
    iurl = url + type_ + '/show/json?id=' + id
    if type_ == 'photo':
        req = requests.get(iurl)
        res = json.loads(req.text).get('data').get('items')
        for index, value in enumerate(res):
            name = id + '.' + str(index) + '.jpg'
            if not os.path.exists(dir + name) and not os.path.exists(dir + 'temp_' + name):
                iiurl = value['img'].replace('type5', 'https://v.bdcache.com')
                # download photo
                threading.Thread(target=bs_spider_download, args=(dir, name, iiurl)).start()
    elif type_ == 'video':
        name = id + '.mp4'
        if not os.path.exists(dir + name) and not os.path.exists(dir + 'temp_' + name):
            req = requests.get(iurl)
            iiurl = json.loads(req.text).get('data').get('vod').replace('type3', 'https://v.bdcache.com').replace('\u0026', '&')
            # download video
            threading.Thread(target=bs_spider_download, args=(dir, name, iiurl)).start()


# download photo / video
@retry
def bs_spider_download(dir, name, iiurl):
    req = requests.get(iiurl, stream=True)
    with open(dir + 'temp_' + name, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    os.rename(dir + 'temp_' + name, dir + name)
    global downloaded
    downloaded = downloaded + 1


# monitor
@retry
def monitor():
    global downloaded
    while True:
        print('\r[{}][threads: {}][downloaded {}] running...'.format(
            time.strftime('%H:%M:%S', time.localtime()),
            len(threading.enumerate()) - 2,
            downloaded
        ), end='')
        time.sleep(0.5)


# main
@retry
def bs_spider(url, type_, by, threadsLimit):
    # create dir
    if not os.path.exists(type_ + '/'):
        os.mkdir(type_ + '/')
    # remove temple file
    for temp in glob.glob(type_ + '/temp_*'):
        os.remove(temp)
    # monitor
    threading.Thread(target=monitor).start()
    for page in range(1, 101):
        # limit the maximum number of threads
        while len(threading.enumerate()) > threadsLimit:
            time.sleep(0.5)
        # download
        bs_spider_page(type_ + '/', url, type_, by, page)


if __name__ == '__main__':
    bs_spider('http://www.dalibox.com/', 'photo', '1', 200)
    bs_spider('http://www.dalibox.com/', 'video', '1', 20)

    input()