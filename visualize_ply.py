import open3d as o3d

# 读取 PLY 文件
path = "/home/cy/Gra_design/FUNSR/outs/case000070.nii_ds/outputs/00015000_0.0.ply"
# pcd = o3d.io.read_point_cloud(path)

pcd = o3d.io.read_triangle_mesh(path)
pcd.compute_vertex_normals()
print(pcd)

# 可视化点云
o3d.visualization.draw_geometries([pcd])