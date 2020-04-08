# -*- coding: UTF-8 -*-
import os
import glob
import time
import json
import requests
import threading
from retrying import retry
import sys
import inspect
import ctypes
import tkinter
import tkinter.messagebox

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


# UI
@retry
def bs_spider_gui():
    root = tkinter.Tk()
    root.title("spider")
    root.geometry("+200+200")
    root.resizable(0, 0)
    # title
    tkinter.Label(root, text="BeautyBox Spider", font=("Microsoft YaHei", 16), width=40, height=3).pack()
    # url
    tkinter.Label(root, text="BASE URL:", font=("Microsoft YaHei", 8), fg="gray", anchor="w", width=60).pack()
    var_url = tkinter.StringVar()
    tkinter.Entry(root, width=56, textvariable=var_url).pack()
    var_url.set("http://www.xxxxxx.com/")
    # type_ by
    var_photo_by1 = tkinter.BooleanVar()
    var_photo_by2 = tkinter.BooleanVar()
    var_photo_by3 = tkinter.BooleanVar()
    var_photo_by4 = tkinter.BooleanVar()
    var_video_by1 = tkinter.BooleanVar()
    var_video_by2 = tkinter.BooleanVar()
    var_video_by3 = tkinter.BooleanVar()
    var_video_by4 = tkinter.BooleanVar()
    frm_type_by = tkinter.Frame(root)
    frm_photo = tkinter.Frame(frm_type_by)
    frm_video = tkinter.Frame(frm_type_by)
    ckb_photo_by1 = tkinter.Checkbutton(frm_photo, text='Top 2000 atlas in one day', variable=var_photo_by1, anchor="w", width=25)
    ckb_photo_by2 = tkinter.Checkbutton(frm_photo, text='Top 2000 atlas in a week', variable=var_photo_by2, anchor="w", width=25)
    ckb_photo_by3 = tkinter.Checkbutton(frm_photo, text='Top 2000 atlas in a month', variable=var_photo_by3, anchor="w", width=25)
    ckb_photo_by4 = tkinter.Checkbutton(frm_photo, text='Top 2000 atlas in all', variable=var_photo_by4, anchor="w", width=25)
    ckb_video_by1 = tkinter.Checkbutton(frm_video, text='Top 2000 videos in a day', variable=var_video_by1, anchor="w", width=25)
    ckb_video_by2 = tkinter.Checkbutton(frm_video, text='Top 2000 videos in a week', variable=var_video_by2, anchor="w", width=25)
    ckb_video_by3 = tkinter.Checkbutton(frm_video, text='Top 2000 videos in a month', variable=var_video_by3, anchor="w", width=25)
    ckb_video_by4 = tkinter.Checkbutton(frm_video, text='Top 2000 videos in all', variable=var_video_by4, anchor="w", width=25)
    tkinter.Label(root, text="MISSIONS:", font=("Microsoft YaHei", 8), fg="gray", anchor="w", width=60).pack()
    frm_type_by.pack()
    frm_photo.pack(side="left")
    ckb_photo_by1.pack()
    ckb_photo_by2.pack()
    ckb_photo_by3.pack()
    ckb_photo_by4.pack()
    frm_video.pack(side="left")
    ckb_video_by1.pack()
    ckb_video_by2.pack()
    ckb_video_by3.pack()
    ckb_video_by4.pack()
    var_photo_by1.set(True)
    # start / stop
    tkinter.Label(root, text="").pack()
    tkinter.Button(root, text="START", font=("Microsoft YaHei", 8), width=25,
                   command=lambda: bs_spider_gui_start(var_url, var_photo_by1, var_photo_by2, var_photo_by3, var_photo_by4, 
                                                       var_video_by1, var_video_by2, var_video_by3, var_video_by4)).pack()
    tkinter.Button(root, text="STOP ( restart program )", font=("Microsoft YaHei", 8), width=25, 
                   command=lambda: bs_spider_gui_stop()).pack()
    # log
    tkinter.Label(root, text="").pack()
    lab_log = tkinter.Label(root, text="ready...", font=("Microsoft YaHei", 8), fg="gray", anchor="w", width=60, height=3)
    lab_log.pack()
    def trickit():
        global downloaded
        if len(threading.enumerate()) - 2 < 0:
            log = "ready..."
        else:
            log = "running... " + str(len(threading.enumerate()) - 2) + ' / ' + str(downloaded)
        lab_log.config(text=log)
        root.update()
        lab_log.after(1000, trickit)
    lab_log.after(1000, trickit)
    # mainloop
    root.mainloop()


# UI Start Download Function
@retry
def bs_spider_gui_start(var_url, var_photo_by1, var_photo_by2, var_photo_by3, var_photo_by4, 
                        var_video_by1, var_video_by2, var_video_by3, var_video_by4):
    if len(threading.enumerate()) - 1 > 0:
        tkinter.messagebox.showwarning('Warnning', 'Program is running.')
    else:
        threading.Thread(target=bs_spider_gui_task, args=(var_url, var_photo_by1, var_photo_by2, var_photo_by3, var_photo_by4, 
                                                          var_video_by1, var_video_by2, var_video_by3, var_video_by4)).start()


# UI Start Download Function
@retry
def bs_spider_gui_task(var_url, var_photo_by1, var_photo_by2, var_photo_by3, var_photo_by4, 
                       var_video_by1, var_video_by2, var_video_by3, var_video_by4):
    if var_photo_by1.get():
        bs_spider(str(var_url.get()), 'photo', '1', 200)
    if var_photo_by2.get():
        bs_spider(str(var_url.get()), 'photo', '7', 200)
    if var_photo_by3.get():
        bs_spider(str(var_url.get()), 'photo', '30', 200)
    if var_photo_by4.get():
        bs_spider(str(var_url.get()), 'photo', '100', 200)
    if var_video_by1.get():
        bs_spider(str(var_url.get()), 'video', '1', 20)
    if var_video_by2.get():
        bs_spider(str(var_url.get()), 'video', '7', 20)
    if var_video_by3.get():
        bs_spider(str(var_url.get()), 'video', '30', 20)
    if var_video_by4.get():
        bs_spider(str(var_url.get()), 'video', '100', 20)
    

# UI Stop Download Function ( restart )
@retry
def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


# UI Stop Download Function ( restart )
@retry
def _stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


# UI Stop Download Function ( restart )
@retry
def bs_spider_gui_stop():
    python = sys.executable
    os.system('cls')
    os.execl(python, python, * sys.argv)


if __name__ == '__main__':
    print('{:=^80}\nBeautyBox Content Downloader\n{:=^80}'.format('', ''))
    bs_spider_gui()