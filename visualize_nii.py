import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 获取初始切片数据
def get_slice(index):
    if slice_mode == 0:
        return data[int(index), :, :]
    elif slice_mode == 1:
        return data[:, int(index), :]
    elif slice_mode == 2:
        return data[:, :, int(index)]


slice_mode = 0  # 0是冠状，1是矢状，2是轴向

path_prefix = "/home/cy/Gra_design/dataset/nii_data/train/us_images/"
data_name = "case000060.nii.gz"
path = path_prefix + data_name

image = nib.load(path)

# affine_matrix = image.affine
# print("仿射矩阵:\n", affine_matrix)

data = image.get_fdata().squeeze() # dim [81,118,81]

# 选择某个切片（轴向、矢状、冠状）
max_index = data.shape[slice_mode] - 1  # 获取最大索引

# 初始化画布
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)  # 预留空间放 slider
slice_index = max_index // 2  # 取中间切片

# 显示初始切片
slice_data = get_slice(slice_index)
img_display = ax.imshow(slice_data.T, cmap="gray", origin="lower")
ax.set_title(f"Slice {slice_index}/{max_index}")

# 添加滑动条 (Slider)
ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor="lightgray")
slider = Slider(ax_slider, "Slice", 0, max_index, valinit=slice_index, valstep=1)

# 更新函数
def update(val):
    slice_index = int(slider.val)
    slice_data = get_slice(slice_index)
    img_display.set_data(slice_data.T)  # 更新图像
    ax.set_title(f"Slice {slice_index}/{max_index}")  # 更新标题
    fig.canvas.draw_idle()  # 刷新

# 绑定滑动条
slider.on_changed(update)

plt.show()


    

