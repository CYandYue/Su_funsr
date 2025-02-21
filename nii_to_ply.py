import nibabel as nib
import numpy as np
import open3d as o3d

slice_data = "val"      # 分为 train 和 val
slice_label = "labels"   # 维度： images [x,y,z,1]  labels [x,y,z,6]

path_prefix = f"/home/cy/Gra_design/dataset/nii_data/{slice_data}/us_{slice_label}/"
data_name = "case000070.nii.gz"
nii_path = path_prefix + data_name

img = nib.load(nii_path)
data = img.get_fdata().squeeze()
data = data[:,:,:,0]

# 2. 找到所有非零体素（点云坐标）
print("Data min:", np.min(data))
print("Data max:", np.max(data))
print("Unique values:", np.unique(data)[:10])  # 仅显示前 10 个唯一值

points = np.argwhere(data == 255)  # 仅保留非零体素
values = data[points[:, 0], points[:, 1], points[:, 2]]  # 获取对应的像素值（可用于颜色）

# 3. 创建 Open3D 点云对象
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

# # 5. 保存为 PLY
# ply_path = "output.ply"
# o3d.io.write_point_cloud(ply_path, pcd)
# print(f"Point cloud saved to {ply_path}")

# 6. 可视化
o3d.visualization.draw_geometries([pcd])
