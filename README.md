## setup
```bash
conda create -n su_funsr python=3.8
conda activate su_funsr
conda install pytorch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 pytorch-cuda=12.1 -c pytorch -c nvidia
python -m pip install pymcubes==0.1.4
pip install tqdm pyhocon==0.3.57 trimesh scipy
pip install matplotlib
pip install open3d
```
for more, refer to [pytorch and other related package version](https://pytorch.org/get-started/previous-versions/).
## Run
```bash
python run_normalizedSpace.py --gpu 0 --conf confs/conf.conf --dataname case000070.nii_ds  --dir case000070.nii_ds
```

```bash
python run_normalizedSpace.py --gpu 0 --conf confs/conf_us_nerf.conf --dataname model_014000  --dir model_014000
```