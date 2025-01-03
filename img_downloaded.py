# img_downloaded.py
# ※※　実行時、python img_downloaded.py "Park Jimin" "Kim Taehyung" ...　のようにキーワードを指定して実行する　※※
# 必要なライブラリのインポート

# face_recognitionの顔検出方法を変更する:model='hog'⇒model='cnn'に変更
# dlibを単体で使って顔認識を行う
# OpenCVのHaar CascadeやDNNベースのモデルを利用して顔検出を行う

import os
import sys
import time
from flickrapi import FlickrAPI
from urllib.request import urlretrieve
import face_recognition
from PIL import Image, ImageDraw
import dlib
import cv2

# 環境変数から Flickr API キーとシークレットを取得
API_KEY = '14b03db163c6f3919cfd7d53bd8b06b0'
SECRET_KEY = '4c7111e346406c0d'

if not API_KEY or not SECRET_KEY:
    print("Error: Missing Flickr API credentials.")
    sys.exit(1)

# ダウンロード間隔（秒）
interval = 1

# 引数からキーワードを取得
if len(sys.argv) < 2:
    print("Usage: python img_download.py <keyword1> <keyword2> ...")
    sys.exit(1)

# キーワードと対応するタグの定義
nicknames = {
    "Park Jimin": "JIMIN",
    "Kim Taehyung": "JIN"
}

# キーワードリストを取得
keywords = sys.argv[1:]
print(f"Downloading images for keywords: {keywords}")

# Flickr API 初期化
flickr = FlickrAPI(API_KEY, SECRET_KEY, format='parsed-json')

# Haar Cascade 顔検出器の読み込み
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# 各キーワードで画像を検索・ダウンロード
for name in keywords:
    nickname = nicknames.get(name, "")
    if not nickname:
        print(f"Warning: No nickname found for '{name}', skipping.")
        continue

    print(f"Processing keyword: {name} (nickname: {nickname})")

    # 保存先ディレクトリ作成
    savedir = f'./images/{name.replace(" ", "_")}'
    filtered_dir = f'{savedir}/filtered'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    if not os.path.exists(filtered_dir):
        os.makedirs(filtered_dir)

    # Flickr API で画像検索
    result = flickr.photos.search(
        text=f"BTS {name} {nickname}",
        tags=f"BTS,{nickname}",
        tag_mode="all",
        per_page=500,
        media="photos",
        sort="relevance",
        safe_search=1,
        extras="url_q, license"
    )

    photos = result.get('photos', {})
    photo_list = photos.get('photo', [])
    print(f"Found {len(photo_list)} photos for '{name}'")

    # 各画像をダウンロード
    error_log = f"{savedir}/error_log.txt"
    for i, photo in enumerate(photo_list):
        url = photo.get('url_q')  # 小サイズ画像のURL
        if not url:
            continue

        filepath = os.path.join(savedir, f"{photo['id']}.jpg")
        print(f"Downloading: {filepath}")

        # すでにダウンロード済みの場合はスキップ
        if os.path.exists(filepath):
            print(f"File already exists: {filepath}")
            continue

        # 画像をダウンロード
        try:
            urlretrieve(url, filepath)
            time.sleep(interval)

        except Exception as e:
            with open(error_log, 'a') as f:
                f.write(f"Failed to download {url}: {e}\n")
            print(f"Failed to process {url}: {e}")

    # 既存の画像をフィルタリング
    print(f"Re-filtering images in directory: {savedir}")
    existing_images = [f for f in os.listdir(savedir) if f.endswith('.jpg')]

    for image_file in existing_images:
        filepath = os.path.join(savedir, image_file)
        try:
            # 顔認識によるフィルタリング
            image = cv2.imread(filepath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 1:
                # 顔が1つだけの場合、フィルタ済みフォルダにコピー
                filtered_path = os.path.join(filtered_dir, os.path.basename(filepath))
                with Image.open(filepath) as img:
                    img.save(filtered_path)
                print(f"Filtered and saved: {filtered_path}")
            else:
                print(f"Skipped: {filepath} (faces detected: {len(faces)})")

        except Exception as e:
            print(f"Failed to process {filepath}: {e}")

print("All downloads and filtering complete.")