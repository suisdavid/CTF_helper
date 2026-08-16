import piexif
from PIL import Image
 
# 加载 JPG 图片
img = Image.open("b.jpg")
 
# 创建新的 EXIF 数据
exif_dict = {
    piexif.ImageIFD.ImageDescription: "新标题",
    piexif.ImageIFD.Make: "相机品牌",
    piexif.ImageIFD.Model: "相机型号",
    piexif.ImageIFD.Software: "编辑软件",
    piexif.ImageIFD.Artist: "作者名",
    piexif.ImageIFD.Copyright: "版权所有信息",
    piexif.ImageIFD.DateTime: "2024:10:01 12:00:00",
}
 
# 将字典转换为二进制 EXIF 数据
exif_bytes = piexif.dump(exif_dict)
 
# 保存带有 EXIF 数据的图片
img.save("output_image.jpg", exif=exif_bytes)
 
print("EXIF 信息已成功添加！")
