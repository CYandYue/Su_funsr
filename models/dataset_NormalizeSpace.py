

import torch
import torch.nn.functional as F
import numpy as np
import os
from scipy.spatial import cKDTree
import trimesh
import open3d as o3d






######Load data############
class Dataset:
    def __init__(self, conf, dataname):
        super(Dataset, self).__init__()
        self.device = torch.device('cuda')
        self.conf = conf

        self.data_dir = conf.get_string('data_dir')
        self.np_data_name = dataname + '.pt'



        if os.path.exists(os.path.join(self.data_dir, self.np_data_name)):
            print('Data existing. Loading data...')
        else:
            print('Data not found. Processing data...')
            self.process_data(self.data_dir, dataname)

        print("Loading from saved data...")
        prep_data = torch.load(os.path.join(self.data_dir, self.np_data_name),map_location=self.device)
        self.point = prep_data["sample_near"]
        self.sample = prep_data["query_points"]
        self.point_gt = prep_data["pointcloud"]


        self.sample_points_num = self.sample.shape[0]-1
        self.object_bbox_min, _  = torch.min(self.point,dim = 0)
        self.object_bbox_min =  self.object_bbox_min - 0.05
        self.object_bbox_max,_  = torch.max(self.point,dim = 0)
        self.object_bbox_max = self.object_bbox_max + 0.05
        print('Data bounding box:',self.object_bbox_min,self.object_bbox_max)


        
        print('NP Load data: End')

    def np_train_data(self, batch_size):
        index_coarse = np.random.choice(10, 1)
        index_fine = np.random.choice(self.sample_points_num//10, batch_size, replace = False)
        index = index_fine * 10 + index_coarse
        points = self.point[index]
        sample = self.sample[index]
        return points, sample, self.point_gt



    ########Convert the .ply file into .npz ############
    def process_data(self,data_dir, dataname):
        if os.path.exists(os.path.join(data_dir, dataname) + '.ply'):
            pointcloud = trimesh.load(os.path.join(data_dir, dataname) + '.ply').vertices
            pointcloud = np.asarray(pointcloud)
        elif os.path.exists(os.path.join(data_dir, dataname) + '.xyz'):
            pointcloud = np.load(os.path.join(data_dir, dataname)) + '.xyz'
        else:
            print('Only support .xyz or .ply data. Please make adjust your data.')
            exit()

        
        shape_scale = np.max([np.max(pointcloud[:,0])-np.min(pointcloud[:,0]),np.max(pointcloud[:,1])-np.min(pointcloud[:,1]),np.max(pointcloud[:,2])-np.min(pointcloud[:,2])])
        shape_center = [(np.max(pointcloud[:,0])+np.min(pointcloud[:,0]))/2, (np.max(pointcloud[:,1])+np.min(pointcloud[:,1]))/2, (np.max(pointcloud[:,2])+np.min(pointcloud[:,2]))/2]
        pointcloud = pointcloud - shape_center
        pointcloud = pointcloud / shape_scale

        pc = self.FPS_sampling(pointcloud,data_dir,dataname)


        pointcloud=torch.from_numpy(pc).to(self.device).float()

        grid_samp = 30000
        def gen_grid(start, end, num):
            x = np.linspace(start,end,num=num)
            y = np.linspace(start,end,num=num)
            z = np.linspace(start,end,num=num)
            g = np.meshgrid(x,y,z)
            positions = np.vstack(map(np.ravel, g))
            return positions.swapaxes(0,1)



        dot5 = gen_grid(-0.5,0.5, 70)
        dot10 = gen_grid(-1.0, 1.0, 50)
        grid = np.concatenate((dot5,dot10))
        # grid = dot5
        grid = torch.from_numpy(grid).to(self.device).float()
        grid_f = grid[ torch.randperm(grid.shape[0])[0:grid_samp] ]


        query_per_point = 20
        query_points = self.sample_query2(query_per_point,pointcloud,pc) 

        # concat sampled points with grid points 
        query_points = torch.cat([query_points, grid_f]).float()
        
        print(query_points.size())

        ## find nearest neiboring point cloud for each query point
        POINT_NUM = 20  # divide by batch to avoid out-of-memory
        query_points_nn = torch.reshape(query_points, (-1, POINT_NUM, 3))
        sample_near_tmp = []
        sample_near = []
        for j in range(query_points_nn.shape[0]):
            nearest_idx = self.search_nearest_point(torch.tensor(query_points_nn[j]).float().cuda(), torch.tensor(pointcloud).float().cuda())
            nearest_points = pointcloud[nearest_idx]
            nearest_points = nearest_points.reshape(-1,3)
            sample_near_tmp.append(nearest_points)
        sample_near_tmp=torch.stack(sample_near_tmp,0)  
        sample_near_tmp = sample_near_tmp.reshape(-1,3)
        sample_near = sample_near_tmp


        print("Saving files...")
        torch.save( {
                    "pointcloud":pointcloud,
                    "query_points":query_points,
                    "sample_near":sample_near,
                    },
                    os.path.join(data_dir, dataname)+'.pt')
    


    def FPS_sampling(self,point_cloud, data_dir,dataname):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(point_cloud.reshape(-1,3))

        pcd_concat = o3d.geometry.PointCloud()

        if len(pcd.points) > 60000:
            pcd_down_1 = pcd.farthest_point_down_sample(5000)  # pcd: CloudPoint
            pcd_down_2 = pcd.farthest_point_down_sample(15000)  # pcd: CloudPoint    else:
            pcdConcat = np.concatenate((np.asarray(pcd_down_1.points), np.asarray(pcd_down_2.points)), axis=0)
            # o3d.io.write_point_cloud(os.path.join(data_dir, dataname)+'_ds.ply', pcd)
        else:
            pcdConcat = np.asarray(pcd.points)

        pcd_concat.points = o3d.utility.Vector3dVector(pcdConcat.reshape(-1,3))

        print("number of points:", len(pcd_concat.points))
        point_cloud_concate = np.asarray(pcd_concat.points)
        return point_cloud_concate

    # find the 50th nearest neighbor for each point in pc 
    # this will be the std for the gaussian for generating query 
    def sample_query(self,query_per_point, pc): 

        # scale = 0.25

        dists = torch.cdist(pc, pc)

        std, _ = torch.topk(dists, 50, dim=-1, largest=False) # shape: 1024, 50

        std = std[:,-1].unsqueeze(-1) # new shape is 1024, 1

        query_points = torch.empty(size=(pc.shape[0]*query_per_point, 3)).to(self.device).float()
        count = 0

        for idx, p in enumerate(pc):

            # query locations from p
            q_loc = torch.normal(mean=0.0, std=std[idx].item(),
                                    size=(query_per_point, 3)).to(self.device).float()

            # query locations in space
            q = p + q_loc

            query_points[count:count+query_per_point] = q

            count += query_per_point

        return query_points

    def sample_query2(self,query_per_point, pc,pointcloud):
        # divide point cloud by bacth to avoid out-of-memory

        ptree = cKDTree(pointcloud)
        std = []
        for p in np.array_split(pointcloud,100,axis=0):
            d = ptree.query(p,51)
            std.append(d[0][:,-1])
        
        std = np.concatenate(std)


        std=torch.from_numpy(std).to(self.device).float()

        std = std.unsqueeze(-1) # new shape is 1024, 1

        query_points = torch.empty(size=(pc.shape[0]*query_per_point, 3)).to(self.device).float()
        count = 0

        for idx, p in enumerate(pc):

            # query locations from p
            q_loc = torch.normal(mean=0.0, std=std[idx].item(),
                                    size=(query_per_point, 3)).to(self.device).float()

            # query locations in space
            q = p + q_loc

            query_points[count:count+query_per_point] = q

            count += query_per_point

        return query_points

    # the closest point in the pc for all query points 
    def find_nearest_query_neighbor(self,pc, query_points):

        dists = torch.cdist(query_points, pc).detach().cpu().numpy()
        min_dist, min_idx = torch.min(dists, dim=-1).detach().cpu().numpy()  
        nearest_neighbors = pc[min_idx]

        return nearest_neighbors, min_dist.unsqueeze(-1)

    ######Find the nearest neighbour points ##########
    def search_nearest_point(self,point_batch, point_gt):
        num_point_batch, num_point_gt = point_batch.shape[0], point_gt.shape[0]
        point_batch = point_batch.unsqueeze(1).repeat(1, num_point_gt, 1)
        point_gt = point_gt.unsqueeze(0).repeat(num_point_batch, 1, 1)

        distances = torch.sqrt(torch.sum((point_batch-point_gt) ** 2, axis=-1) + 1e-12) 
        dis_idx = torch.argmin(distances, axis=1).detach().cpu().numpy()

        return dis_idx