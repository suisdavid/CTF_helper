import numpy as np
from scipy.io import wavfile
from scipy.signal import hilbert
from PIL import Image

fs, x = wavfile.read("chaos.wav")
x = x.astype(np.float64) / 32768.0

# 瞬时频率
inst = np.diff(np.unwrap(np.angle(hilbert(x)))) * fs / (2 * np.pi)
inst = np.clip(inst, 500, 3000)

# 找 1200Hz sync pulse
sync_sm = np.convolve(inst, np.ones(int(fs * 0.005)) / int(fs * 0.005), "same")
mask = (sync_sm > 1150) & (sync_sm < 1250)

pos = np.r_[0, np.flatnonzero(np.diff(mask.astype(int)) != 0) + 1, len(mask)]
syncs = []

for v, s, l in zip(mask[pos[:-1]], pos, np.diff(pos)):
    t = s / fs
    dur = l / fs
    if v and dur > 0.01 and t > 0.85:
        syncs.append((s / fs, (s + l) / fs, dur))

# PD120 参数
W, H = 640, 496
porch = 0.00208
ydur = 0.160
cdur = 0.080

cs = np.concatenate([[0.0], np.cumsum(inst)])

def sample_avg(t0, dur, n):
    starts = ((t0 + (np.arange(n) + 0.1) * dur / n) * fs).astype(int)
    ends   = ((t0 + (np.arange(n) + 0.9) * dur / n) * fs).astype(int)

    starts = np.clip(starts, 0, len(inst) - 1)
    ends = np.clip(ends, starts + 1, len(inst))

    freq = (cs[ends] - cs[starts]) / (ends - starts)

    # SSTV: 1500Hz 黑，2300Hz 白
    return np.clip((freq - 1500) / 800 * 255, 0, 255).astype(np.uint8)

img = np.zeros((H, W), dtype=np.uint8)

for i in range(248):
    t = syncs[i][1] + porch

    y1 = sample_avg(t, ydur, W)
    t += ydur + porch

    # chroma 1，灰度图可跳过
    t += cdur + porch

    y2 = sample_avg(t, ydur, W)

    img[2 * i] = y1
    img[2 * i + 1] = y2

Image.fromarray(img).save("pd120_gray.png")
