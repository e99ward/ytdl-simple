from __future__ import unicode_literals
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox
from PyQt5.QtGui import QPixmap, QIcon

import yt_dlp
import urllib
import time

## v.0: guide from yt-dpl package
## v.1: get info about formats --> actually no need
## v.2: select formats from the list
## v.3: pyQT
## v.4: connect

# # URL = 'https://youtu.be/7m9dNmpCkPI'
# URL = 'https://youtu.be/Cxzzg7L3Xgc'

# GOTO C:\Users\taiji\Documents\VS Code\Python Scripts\ytdl>
# C:\Users\taiji\AppData\Local\Programs\Python\Python39\Scripts\pyinstaller.exe -w -F ytdlp.py

formats = [{'name': 'Best quality', 'format': 'bestvideo+bestaudio/best'},
           {'name': 'QHD (1440p)', 'format': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]'},
           {'name': 'FHD (1080p)', 'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'},
           {'name': 'HD (720p)', 'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]'},
           {'name': 'VGA (480p)', 'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]'}]
# UHD(2160p), QHD, FHD, HD, VGA


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

# sel = input('0: UHD / 1: QHD / 2: FHD / 3: HD / 4: VGA')
# target_format = formats[int(sel)]
# opt2 = {
#     'format': 'bestaudio/best',
#     'audioformat': 'mp3',
#     'extractaudio' : True, 
#     'noplaylist': True,
#     'outtmpl': '/downloadtest/%(title)s.%(ext)s',
#     'writethumbnail': 'true',
#     'postprocessors': [{
#         'key': 'FFmpegExtractAudio',
#         'preferredcodec': 'mp3',
#         'preferredquality': '192', # actually 64 -> made to 192 TT
#     }, {
#         'key': 'FFmpegMetadata'
#     }, {
#         'key': 'EmbedThumbnail'
#     }],
#     'logger': MyLogger(),
#     'progress_hooks': [my_hook],  
# }
#
# # ydl_opts = {}
# #
# # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
# #     info = ydl.extract_info(URL, download=False)
# #     video_id = info.get('id', None)
# #     video_title = info.get('title', None)
# #     formats = info.get('formats', [info])
# #     for f in formats:
# #         #if f['protocol'] == 'https':
# #         #    print(f['format_id'],f['protocol'], f['vcodec'])
# #         print(f['format_id'],f['resolution'],f['ext'],f['vcodec']) #f['format']
# 
# #with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     #ydl.add_post_processor(filename_collector)
#     

class Downloader(QThread):

    status = pyqtSignal(list)
    complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.order = False
        self.detail = False     # view details
        self.option = 0         # download format options
        self.URL = ''           # video address

    def run(self):
        # Load Lotto DB
        # global nm_in_db
        print('download thread is working....')
        while True:
            if self.order:
                print("start")
                if self.detail:
                    info = self.get_video_details()
                    self.status.emit(info)
                self.get_video()
                print('completed!!')
                self.complete.emit()
                self.order = False
                # break
            time.sleep(3) # magical three seconds
        # print('completed!!')
        # self.complete.emit(nPred)

    def __del__(self):
        print("...end thread")

    @pyqtSlot()
    def GoDownload(self):
        print("...do download")
        self.order = True

    def get_video(self):
        ydl_opts = {
            'ignoreerrors': True,
            'nooverwrites': True,
            # 'skip_download': True,
            'noplaylist': True,
            'format': formats[self.option]['format'],
            'outtmpl': '%(title)s.%(ext)s',        
            'postprocessors': [{'key': 'FFmpegMerger',}],
            'merge_output_format': 'webm',
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],  
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.URL])

    def get_video_details(self):
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.URL, download=False)
            video_id = info.get('id', None)
            video_title = info.get('title', None)

            return [video_id, video_title]

    def my_hook(self, d):
        if d['status'] == 'finished':
            print('file name:', d['filename'], 'file size bytes:', d['total_bytes'])
            print('Done downloading, now converting...')


class App(QWidget):

    do_download_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.worker = Downloader()
        # self.thread = QThread()
        # self.thread.started.connect(self.worker.run)
        self.title = 'YouTube Downloader'
        self.left = 100
        self.top = 100
        self.width = 700
        self.height = 500
        fontD = self.font()
        fontD.setPointSize(10)
        fontD.setFamilies(['나눔바른고딕', '맑은 고딕', 'Segoe UI', 'NanumBarunGothic'])
        self.window().setFont(fontD)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # inputs from user
        self.urlText = QLineEdit()
        self.urlText.setPlaceholderText('Enter YouTube URL')
        self.urlText.setText('') #set default video to download
        # urlEntryText.textChanged.connect(self.resetVideoFormats) #set up callback to update video formats when URL is changed
        self.optionFormats = QComboBox()
        self.optionFormats.clear()
        for f in formats:
            self.optionFormats.addItem(f['name'])
        #self.populateVideoFormatCombobox(self.default_video_formats_menu_items) #set default values for format select combobox
        #self.videoFormatCombobox.activated[str].connect(self.videoFormatChange)
        self.details = QCheckBox('View video thumbnail')
        # 
        inputs = QGridLayout()
        inputs.addWidget(QLabel('URL:'), 0, 0)
        inputs.addWidget(self.urlText, 0, 1)
        inputs.addWidget(QLabel('Options:'), 1, 0)
        inputs.addWidget(self.optionFormats, 1, 1)
        inputs.addWidget(self.details, 2, 1)

        # details about video
        # thumbnail, title, ID, etc.
        view = QVBoxLayout()
        self.thumbnail = QLabel(self)
        #pixmap = QPixmap('image.jpg')
        pixmap = QPixmap('./mainlogo.jpg')
        self.thumbnail.setPixmap(pixmap.scaledToHeight(150))
        self.thumbnail.setFixedHeight(160)
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.videotitle = QLabel('by e99ward')
        self.videotitle.setAlignment(Qt.AlignCenter)
        view.addWidget(self.thumbnail)
        view.addWidget(self.videotitle)

        #thumbnail.move(200,0)

        # download button
        self.btnDownload = QPushButton('Download', self)
        self.btnDownload.setFixedHeight(60)
        self.btnDownload.clicked.connect(self.do_Download)
        # downloadButton.clicked.connect(self.downloadVideo_callback)

        self.worker.start()
        self.do_download_signal.connect(self.worker.GoDownload)
        self.worker.status.connect(self.ViewDetails)
        self.worker.complete.connect(lambda: update_button())
        @pyqtSlot()
        def update_button():
            self.btnDownload.setEnabled(True)
            self.btnDownload.setText('Download')

        layout = QVBoxLayout()
        layout.addSpacing(10)
        layout.addLayout(inputs)
        layout.addLayout(view)
        layout.addWidget(self.btnDownload)
        self.setLayout(layout)
        self.show()
        
    @pyqtSlot(list)
    def ViewDetails(self, info):
        v_ID = info[0]
        v_title = info[1]
        urlString = 'https://i.ytimg.com/vi/' + v_ID + '/hqdefault.jpg'
        imageWeb = urllib.request.urlopen(urlString).read()
        pixmap = QPixmap()
        pixmap.loadFromData(imageWeb)
        self.thumbnail.setPixmap(pixmap.scaledToHeight(150))
        self.thumbnail.setFixedHeight(160)
        self.videotitle.setText(v_title)

    def do_Download(self):
        self.btnDownload.setEnabled(False)
        self.btnDownload.setText('downloading...')
        self.worker.detail = self.details.isChecked()
        self.worker.option = self.optionFormats.currentIndex()
        self.worker.URL = self.urlText.text()
        self.do_download_signal.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
