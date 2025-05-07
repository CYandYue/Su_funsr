import open3d as o3d
from pyntcloud import PyntCloud

mode = "pcd"
# mode = "mesh"

path_prefix = "/home/cy/Gra_design/FUNSR/outs/case000070.nii_ds/outputs/"
ply_name = "00015000_0.0.ply"
path = path_prefix + ply_name

# path = "/home/cy/Gra_design/FUNSR/data/case000070.nii_ds.ply"

# path = "/home/cy/Gra_design/us_nerf_pro/compounding_result_ply/spine_phantom_left2/model_012000.ply"

# path = "/home/cy/Gra_design/FUNSR/outs/model_012000/outputs/00015000_0.0.ply"



if mode == "pcd":
    # pcd = o3d.io.read_point_cloud(path)
    # print(pcd)
    
    # o3d.visualization.draw_geometries([pcd])
    
    cloud = PyntCloud.from_file(path)
    # 可视化点云
    cloud.plot()
    
elif mode == "mesh":
    mesh = o3d.io.read_triangle_mesh(path)
    print(mesh)
    
    # 算一下法向量来渲染
    mesh.compute_vertex_normals()
    
    o3d.visualization.draw_geometries([mesh])
