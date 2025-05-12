import matplotlib.pyplot as plt

# 数据
epochs = [2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 18000]
ious = [0.8898, 0.8732, 0.8900, 0.8357, 0.8546, 0.8487, 0.8303, 0.8349, 0.8379]
dscs = [0.8949, 0.8864, 0.8950, 0.8668, 0.8768, 0.8737, 0.8639, 0.8663, 0.8680]
asds = [2.5638, 2.4563, 3.1062, 4.2213, 3.1829, 3.8640, 4.3734, 3.8061, 3.2713]

# 通用字体设置
font = {'size': 16}
plt.rc('font', **font)

# IoU vs Epoch
plt.figure(figsize=(8, 5))
plt.plot(epochs, ious, marker='o', linestyle='-', color='blue')
plt.title("IoU vs Epoch", fontsize=18)
plt.xlabel("Epoch", fontsize=16)
plt.ylabel("IoU", fontsize=16)
plt.grid(True)
plt.tight_layout()
plt.show()

# DSC vs Epoch
plt.figure(figsize=(8, 5))
plt.plot(epochs, dscs, marker='s', linestyle='-', color='green')
plt.title("Dice Similarity Coefficient vs Epoch", fontsize=18)
plt.xlabel("Epoch", fontsize=16)
plt.ylabel("DSC", fontsize=16)
plt.grid(True)
plt.tight_layout()
plt.show()

# ASD vs Epoch
plt.figure(figsize=(8, 5))
plt.plot(epochs, asds, marker='^', linestyle='-', color='red')
plt.title("Average Surface Distance (ASD) vs Epoch", fontsize=18)
plt.xlabel("Epoch", fontsize=16)
plt.ylabel("ASD", fontsize=16)
plt.grid(True)
plt.tight_layout()
plt.show()
