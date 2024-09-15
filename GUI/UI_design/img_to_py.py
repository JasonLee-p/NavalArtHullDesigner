"""
    This file is used to store images in the PTB-BlueprintReader app.
"""

import base64
import os

if __name__ == '__main__':
    # 删除旧的
    if os.path.exists('ImgPng_day.py'):
        os.remove('ImgPng_day.py')
    if os.path.exists('ImgPng_night.py'):
        os.remove('ImgPng_night.py')
    with open('ImgPng_day.py', 'a') as f:
        f.write('"""This file is used to store images in the PTB-BlueprintReader app."""\n\n')
        # 只找images内的文件
        for file in os.listdir('ImgPngDay'):
            if file.endswith('.png'):
                with open(os.path.join('ImgPngDay', file), 'rb') as img:
                    img_base64 = base64.b64encode(img.read())
                    f.write(f'_{file[:-4]} = {img_base64}\n\n')
    with open('ImgPng_night.py', 'a') as f:
        f.write('"""This file is used to store images in the PTB-BlueprintReader app."""\n\n')
        # 只找images内的文件
        for file in os.listdir('ImgPngNight'):
            if file.endswith('.png'):
                with open(os.path.join('ImgPngNight', file), 'rb') as img:
                    img_base64 = base64.b64encode(img.read())
                    f.write(f'_{file[:-4]} = {img_base64}\n\n')
    print('Done!')
