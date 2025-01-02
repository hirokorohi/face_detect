# load_image.py
# 2.画像の前処理
# 画像を読み込んでNumPy形式に変換し、学習用とテスト用に分割して保存する

from PIL import Image
import os, glob
import numpy as np
import warnings

# NumPyの警告を無視する
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# 画像が保存されているディレクトリのパス
image_path = './images'
files = os.listdir(image_path)

dirs = []
for f in files:
    if os.path.isdir(os.path.join(image_path, f)):
        dirs.append(f)
print(dirs)

image_size = 50
num_images = 200
num_testdata = 50

# 学習用画像とテスト画像を保存する配列を宣言
x_train = []
x_test = []
y_train = []
y_test = []

# ディレクトリでループして画像を読み込む
for index, label in enumerate(dirs):
    photos_dir = os.path.join(image_path, label)
    photos = glob.glob(os.path.join(photos_dir, '*.jpg'))
    
    for i, p in enumerate(photos):
        if i >= num_images:
            break
        try:
            image = Image.open(p)
            image = image.convert('RGB')
            image = image.resize((image_size, image_size))
            data = np.asarray(image)

            if i < num_testdata:
                x_test.append(data)
                y_test.append(index)
            else:
                for angle in range(-20, 21, 5):
                    # 5度ずつ-20度から20度まで回転した画像を生成
                    r_image = image.rotate(angle)
                    data = np.asarray(r_image)
                    x_train.append(data)
                    y_train.append(index)

                    # 左右反転した画像を生成
                    t_image = r_image.transpose(Image.FLIP_LEFT_RIGHT)
                    data = np.asarray(t_image)
                    x_train.append(data)
                    y_train.append(index)

        except Exception as e:
            print(f'Error processing {p}: {e}')
            continue        

x_train = np.array(x_train)
x_test = np.array(x_test)
y_train = np.array(y_train)
y_test = np.array(y_test)

xy = (x_train, x_test, y_train, y_test)
print(len(x_train), len(x_test))

print(f"x_train shape: {np.shape(x_train)}")
print(f"x_test shape: {np.shape(x_test)}")
print(f"y_train shape: {np.shape(y_train)}")
print(f"y_test shape: {np.shape(y_test)}")

np.savez(os.path.join(image_path, 'image_data.npz'), 
         x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)


data = np.load(os.path.join(image_path, 'image_data.npz'))
x_train = data['x_train']
x_test = data['x_test']
y_train = data['y_train']
y_test = data['y_test']