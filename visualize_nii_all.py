import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 获取初始切片数据
def get_slice(index, slice_mode, slice_label, data):
    if slice_label == "images":
        if slice_mode == 0:
            return data[int(index), :, :]
        elif slice_mode == 1:
            return data[:, int(index), :]
        elif slice_mode == 2:
            return data[:, :, int(index)]
    elif slice_label == "labels":
        if slice_mode == 0:
            return data[int(index), :, :, 0]
        elif slice_mode == 1:
            return data[:, int(index), :, 0]
        elif slice_mode == 2:
            return data[:, :, int(index), 0]
    else:
        print("slice_data is wrong!")

# 通用字体设置
font = {'size': 16}
plt.rc('font', **font)


slice_mode = 0          # 0是冠状，1是矢状，2是轴向
slice_folder = "val"      # 分为 train 和 val
slice_label = "both"   # 维度： images [x,y,z,1]  labels [x,y,z,6]
data_name = "case000070.nii.gz"

prefix_1 = f"/home/cy/Gra_design/dataset/nii_data/{slice_folder}/us_images/"
prefix_2 = f"/home/cy/Gra_design/dataset/nii_data/{slice_folder}/us_labels/"
path_1 = prefix_1 + data_name
path_2 = prefix_2 + data_name

image = nib.load(path_1)
label = nib.load(path_2)

data_image = image.get_fdata().squeeze() # dim [81,118,81,1]
data_label = label.get_fdata().squeeze() # dim [81,118,81,6]

max_index = data_image.shape[slice_mode] - 1  # 获取最大索引
slice_index = max_index // 2  # 取中间切片

fig, ax = plt.subplots(1, 3 if slice_label == "both" else 1, figsize=(10, 5))
plt.subplots_adjust(bottom=0.25)  # 预留空间放 slider

# 显示初始切片
if slice_label == "both":
    image_1 = get_slice(slice_index, 0, "images", data_image)
    image_2 = get_slice(slice_index, 1, "images", data_image)
    image_3 = get_slice(slice_index, 2, "images", data_image)
    image_display = ax[0].imshow(image_1.T, cmap="gray", origin="lower")
    label_display = ax[1].imshow(image_2, cmap="gray", origin="lower")
    label_display = ax[2].imshow(image_3, cmap="gray", origin="lower")
    ax[0].set_title(f"Coronal Plane ")
    ax[1].set_title(f"Sagittal Plane ")
    ax[2].set_title(f"Transverse Plane ")
else:
    slice_data = get_slice(slice_index, slice_mode, slice_label, data_image if slice_label == "images" else data_label)
    img_display = ax.imshow(slice_data.T, cmap="gray", origin="lower")
    ax.set_title(f"Slice {slice_index}/{max_index}")
    
# 添加滑动条 (Slider)
ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor="lightgray")
slider = Slider(ax_slider, "Slice", 0, max_index, valinit=slice_index, valstep=1)

# 更新函数
def update(val):
    slice_index = int(slider.val)
    if slice_label == "both": 
        image_1 = get_slice(slice_index, 0, "images", data_image)
        image_2 = get_slice(slice_index, 1, "images", data_image)
        image_3 = get_slice(slice_index, 2, "images", data_image)
        image_display = ax[0].imshow(image_1.T, cmap="gray", origin="lower")
        label_display = ax[1].imshow(image_2, cmap="gray", origin="lower")
        label_display = ax[2].imshow(image_3, cmap="gray", origin="lower")
        ax[0].set_title(f"Coronal Plane image {slice_index}/{max_index}")
        ax[1].set_title(f"Sagittal Plane image {slice_index}/{max_index}")
        ax[2].set_title(f"Transverse Plane image {slice_index}/{max_index}")
    else:
        slice_data = get_slice(slice_index, slice_mode, slice_label, data_image if slice_label == "images" else data_label)
        img_display.set_data(slice_data.T)  # 更新图像
        ax.set_title(f"Slice {slice_index}/{max_index}")  # 更新标题
        
    fig.canvas.draw_idle()  # 刷新

# 绑定滑动条
slider.on_changed(update)

plt.show()


    

