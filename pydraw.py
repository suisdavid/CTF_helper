import matplotlib.pyplot as plt

# 从日志中提取的第一个触摸点 (SLOT 0) 的部分关键坐标 (X, Y)
# 数据来源：你提供的文件中的前几个点

def get_coordinates(filename):
    res=[]
    with open(filename,'r') as f:
        s=f.readlines()
        x=0
        y=0
        flg=0
        for each in s:
            tp=int(each[24:28],16)
            val=int(each[29:37],16)
            if tp==0x35:
                if x!=val:
                    flg=1
                x=val
            elif tp==0x36:
                if y!=val:
                    flg=1
                y=val
            elif tp==0 and flg:
                res.append((x,y))
                flg=0
    return res
#coordinates = get_coordinates("event.txt")[:2000]
coordinates = [
    (173, 539), (166, 561), (156, 592), (143, 640), (137, 668),
    (133, 693), (130, 714), (127, 736), (125, 749), (123, 762),
    (122, 773), (120, 782), (118, 790), (116, 797), (114, 803),
    (114, 803), (112, 802), (112, 802), (114, 799), (117, 795),
    (122, 789), (128, 782), (134, 776), (141, 770), (148, 764),
    (155, 760), (163, 757), (170, 756), (177, 756), (183, 758),
    (189, 761), (195, 766), (201, 772), (206, 780), (211, 788),
    (215, 796), (218, 804), (220, 812), (221, 819), (221, 825),
    (220, 830), (218, 835), (215, 840), (211, 845), (206, 849),
    (200, 853), (193, 857), (186, 861), (179, 864), (172, 867),
    (165, 869), (158, 871), (151, 873), (144, 875), (138, 876),
    (133, 877), (128, 878), (124, 879), (121, 880), (119, 881),
    (118, 882), (117, 883), (116, 884), (116, 885)
]
print(len(coordinates))
# 分离 X 和 Y 坐标
x_coords = [p[0] for p in coordinates]
y_coords = [p[1] for p in coordinates]

# 创建绘图
plt.figure(figsize=(20, 16))

# 绘制轨迹线，用颜色深浅表示时间顺序
points = plt.scatter(x_coords, y_coords)
#plt.plot(x_coords, y_coords)



# 图表装饰
plt.title('Touchscreen Gesture Track (SLOT 0)')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.gca().invert_yaxis() # 因为屏幕坐标通常原点在左上角，Y轴向下增加

# 显示图表
plt.show()
