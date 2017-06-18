"""
Copyright (c) 2017, Iruyan_Zak.
License: MIT (see LICENSE for details)
"""

from bottle import run, route, static_file, url, jinja2_template as template


@route('/static/<filepath:path>', name='static_file')
def static(filepath):
    return static_file(filepath, root='./view')


@route('/media/<filepath:path>', name='static_file')
def media(filepath):
    return static_file(filepath, root='./media')


@route('/')
def index():
    return template("view/index.html", img="", music="", debug=["サーバ残り容量： {}".format(get_disk_space())], url=url)


@route('/<screen_name>/<source_url:path>')
def index(screen_name, source_url):
    print(screen_name, source_url)
    if screen_name[0] == '@':
        screen_name = screen_name[1:]

    img_url, debug_info1 = get_twitter_icon_url(screen_name)
    music_path, debug_info2 = get_music(source_url)

    debug_info = debug_info1 + debug_info2
    if img_url and music_path:
        debug_info.append("準備完了！")

    print(debug_info)
    return template("view/index.html", img=img_url, music=music_path, debug=debug_info, url=url)


def get_twitter_icon_url(screen_name):
    from requests import get
    from bs4 import BeautifulSoup

    debug_info = ["[アイコン取得] 開始"]

    twitter_profile_url = "https://twitter.com/{}".format(screen_name)
    debug_info.append("[アイコン取得] URL: {}".format(twitter_profile_url))
    response = get(twitter_profile_url)

    debug_info.append("[アイコン取得] ステータスコード: {}".format(response.status_code))
    if response.status_code != 200:
        return "", debug_info

    soup = BeautifulSoup(response.content, 'html.parser')
    img = soup.find(class_='ProfileAvatar-image')

    if not img:
        debug_info.append("[アイコン取得] アイコンを含むタグがありません。")
        return "", debug_info

    img_url = img.get('src')

    if not img_url:
        debug_info.append("[アイコン取得] アイコンの画像リンクが取得できません。\n{}".format(img_url))
        return "", debug_info

    debug_info.append("[アイコン取得] 完了: {}".format(img_url))
    return img_url, debug_info


def get_music(source_id):
    from youtube_dl import YoutubeDL, DownloadError
    from os.path import exists

    debug_info = ["[音声取得] 開始"]

    dist = "media/{}.mp3".format(source_id)
    if exists(dist):
        debug_info.append("[音声取得] 指定された曲はライブラリの中に見つかりました。")
        dist = '/{}'.format(dist)
        return dist, debug_info

    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            global dist
            debug_info.append("[音声取得] 動画ダウンロード中にエラー: {}".format(msg))
            dist = ''

    def on_complete(d):
        if d['status'] == 'finished':
            debug_info.append("[音声取得] 動画ダウンロード完了。")

    ydl_opts = {
        'outtmpl': "media/{}.%(ext)s".format(source_id),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '160',
        }],
        'logger': MyLogger(),
        'progress_hooks': [on_complete],
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(['https://youtu.be/{}'.format(source_id)])
        except DownloadError:
            debug_info.append("[音声取得] ダウンロードに失敗しました。")
            return '', debug_info

    if dist:
        dist = '/{}'.format(dist)
        debug_info.append("[音声取得] 音声変換完了: {}".format(dist))

    return dist, debug_info


def get_disk_space():
    from shutil import disk_usage

    free_bytes = disk_usage(".").free
    if free_bytes > 1e9:
        return "{0:.2f} GB".format(free_bytes / 1e9)
    return "{} MB".format(int(free_bytes / 1e6))


if __name__ == "__main__":
    from os import makedirs
    from bottle import debug
    makedirs('media', exist_ok=True)
    debug(True)

    run(host='localhost', port=8080, reloader=True)


"""
def hoge():
    import youtube_dl
    import re
    from os.path import exists

    url = 'https://www.youtube.com/watch?v=CWz_SjJSK9s'
    output = re.search(r'(?:v=|youtu\.be/)(.*)', url).group(1)

    if exists("media/{}.mp3".format(output)):
        print("その曲知ってる！")
        return

    class MyLogger(object):
        def debug(self, msg):
            print(msg)

        def warning(self, msg):
            print(msg)

        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    ydl_opts = {
        'outtmpl': 'media/{}.%(ext)s'.format(output),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '160',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("function end.")
"""

