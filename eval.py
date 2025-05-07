import open3d as o3d
import numpy as np
from scipy.spatial import cKDTree

model_folder = "case000070.nii_ds"
model_name = "00015000_0.0.ply"
gt_name = "case000070_GT.ply"

model_folder = "model_012000"
model_name = "00015000_0.0.ply"
gt_name = "model_012000.ply"

gt_path = f"/home/cy/Gra_design/FUNSR/outs/GT/{gt_name}"
train_path = f"/home/cy/Gra_design/FUNSR/outs/{model_folder}/outputs/{model_name}"

# 加载 PLY 文件
pcd1 = o3d.io.read_point_cloud(gt_path)
pcd2 = o3d.io.read_point_cloud(train_path)

points1 = np.asarray(pcd1.points)
points2 = np.asarray(pcd2.points)

# 设置一个距离阈值判断两个点是否“重合”
threshold = 0.01  # 可根据点云密度调整

# KDTree 查找最邻近点
tree1 = cKDTree(points1)
tree2 = cKDTree(points2)

distances1, _ = tree2.query(points1, k=1)
distances2, _ = tree1.query(points2, k=1)

# 计算交集（互为最近点且距离小于阈值）
intersection1 = np.sum(distances1 < threshold)
intersection2 = np.sum(distances2 < threshold)
intersection = (intersection1 + intersection2) / 2

# 联集
union = len(points1) + len(points2) - intersection

# IoU 和 Dice
iou = intersection / union
dsc = (2 * intersection) / (len(points1) + len(points2))

# ASD
asd = (np.mean(distances1) + np.mean(distances2)) / 2

print(f"IoU: {iou:.4f}")
print(f"Dice Similarity Coefficient: {dsc:.4f}")
print(f"Average Surface Distance (ASD): {asd:.4f}")
