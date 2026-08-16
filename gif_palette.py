from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# 加载
gif = Image.open("CHALL.gif")
gif.seek(0)  # 跳到第一帧

# 获取数据
frame = np.array(gif)
palette = gif.getpalette()
print(palette)
# 提取水区域 (下半部分)
water = frame
print(water)
# 提取隐藏的 flag (索引为1的像素)
flag_mask = (water == 1)
print(flag_mask)
# 显示
plt.figure(figsize=(12, 4))
plt.imshow(flag_mask, cmap='gray')
plt.title("Flag: UMASS{IN_A_GIF774}")
plt.axis('off')
plt.show()
