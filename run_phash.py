import math
import argparse
from tqdm import tqdm
from pathlib import Path
from shutil import copy

from clustering import clustering
from imagededup.methods import PHash

# IMG_EXTS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
# IMG_EXTS = [ e.lower() for e in IMG_EXTS]
# IMG_EXTS.extend( [ e.upper() for e in IMG_EXTS ])

parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Path to root directory of images')
parser.add_argument('--thresh', help='distance threshold (hamming distance) int between 0 and 64. Default: 10', default=10, type=int)
parser.add_argument('--get-clusters', help='if flagged, will copy images over to <input name>_Dups_thresh{thresh} output folder in their computed clusters', action='store_true')
parser.add_argument('--dedup', help='if flagged, will copy images over to <input name>_deduped with images randomly sampled ', action='store_true')
args = parser.parse_args()

dist_thresh = int(args.thresh)
assert 0 <= dist_thresh <=64

root_dir = Path(args.directory)
assert root_dir.is_dir()

out_dir = root_dir.parent / 'Dups_thresh{}'.format(dist_thresh)

phasher = PHash()
# imgpaths = [p for p in root_dir.rglob('*') if p.suffix in IMG_EXTS ]
# encoding_map = {}
# for imgpath in tqdm(imgpaths):
# for imgpath in root_dir.rglob('*'):
    # if imgpath.suffix in IMG_EXTS:
        # encoding = phasher.encode_image(image_file=str(imgpath))
        # encoding_map[str(imgpath)] = encoding

encoding_map = phasher.encode_images(image_dir=root_dir, rglob=True)
distance_map = phasher.find_duplicates(encoding_map=encoding_map, max_distance_threshold=dist_thresh, scores=True)

clusters = clustering(distance_map)

print('Original number of images:', len(encoding_map))
print('Num of clusters:', len(clusters))
cluster_counts = [ len(x) for x in clusters ]
print('Clusters size distribution:', cluster_counts)

if args.get_clusters:
    clusters_out_dir = root_dir.parent / '{}_Dups_thresh{}'.format(root_dir.stem, dist_thresh)
    print('Generating clusters at ', clusters_out_dir)
    for cluster_idx, cluster in enumerate(clusters):
        cluster_dir = clusters_out_dir / '{}'.format(cluster_idx)
        cluster_dir.mkdir(exist_ok=True, parents=True)
        for fn in cluster:
            src_path = root_dir / fn
            copy(src_path, cluster_dir) 

if args.dedup:
    import random

    out_dir = root_dir.parent / '{}_deduped'.format(root_dir.stem)
    out_dir.mkdir(exist_ok=True, parents=True)
    print('Generating deduplicated images at', )
    sampling = int(input('Pls give max num of samples you want from each clusters: '))

    sampled_count = 0
    for cluster in clusters:
        if len(cluster) > sampling:
            sampled = random.sample(cluster, k=sampling)
        else:
            sampled = cluster
        
        for fn in sampled:
            src_path = root_dir / fn
            copy(src_path, out_dir) 
            sampled_count += 1
    print('Sampled total count: ', sampled_count)
