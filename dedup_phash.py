import time
import argparse
from pathlib import Path
from shutil import copy, move, rmtree

from clustering import clustering
from imagededup.methods import PHash

# IMG_EXTS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
# IMG_EXTS = [ e.lower() for e in IMG_EXTS]
# IMG_EXTS.extend( [ e.upper() for e in IMG_EXTS ])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Path to root directory of images')
    parser.add_argument('--thresh', help='distance threshold (hamming distance) int between 0 and 64. Default: 10', default=10, type=int)
    parser.add_argument('--move', help='if flagged, will MOVE (instead of copy) images over when dedup is flagged', action='store_true')
    parser.add_argument('--cluster-num', help='max num of samples from each cluster (if dedup is flagged).', type=int)
    parser.add_argument('--extra_dir', help='extra dir names to dedup according', type=str, nargs='*')
    parser.add_argument('--extra_ext', help='extra extensions accordingly to extra_dir', type=str, nargs='*')

    cache_group = parser.add_mutually_exclusive_group()
    cache_group.add_argument('--save', help='save encoding map (phash of images) as pkl', action='store_true')
    cache_group.add_argument('--load', help='load encoding map (phash of images) from pkl', type=str)
    args = parser.parse_args()

    if args.extra_ext:
        assert len(args.extra_ext) == len(args.extra_dir)

    dist_thresh = int(args.thresh)
    assert 0 <= dist_thresh <=64

    root_dir = Path(args.directory)
    assert root_dir.is_dir()

    phasher = PHash()

    if args.load is not None and Path(args.load).is_file():
        import pickle
        encoding_map = pickle.load(open(args.load, 'rb'))
        print(f'Encoding map loaded from pickle file: {args.load}!')
    else:
        tic = time.perf_counter()
        encoding_map = phasher.encode_images(image_dir=root_dir, rglob=True)
        toc = time.perf_counter()
        print(f'encoding duration: {toc-tic:.3f}s')
        if args.save:
            import pickle
            pickle_file = f"{root_dir.stem}_encoding_map.pkl"
            pickle.dump(encoding_map, open(pickle_file,"wb"))
            print(f'Encoding map dumped as pickle at: {pickle_file}')

    tic = time.perf_counter()
    distance_map = phasher.find_duplicates(encoding_map=encoding_map, max_distance_threshold=dist_thresh, scores=True)
    toc = time.perf_counter()
    print(f'find dups duration: {toc-tic:.3f}s')

    tic = time.perf_counter()
    clusters = clustering(distance_map)
    toc = time.perf_counter()
    print(f'clustering duration: {toc-tic:.4f}s')

    print('Original number of images:', len(encoding_map))
    print('Num of clusters:', len(clusters))
    cluster_counts = [ len(x) for x in clusters ]
    print('Clusters size distribution:', cluster_counts)

    import random

    random.seed(88)

    orig_dir = root_dir.parent / f'{root_dir.stem}-dups'
    move(root_dir, orig_dir)

    extra_dirs = []
    renamed_extra_dirs = []
    for extra in args.extra_dir: 
        extra_dir = root_dir.parent / f'{extra}'
        rename_extra = root_dir.parent / f'{extra}-dups'
        
        move(extra_dir, rename_extra)
        extra_dir.mkdir(exist_ok=True, parents=True)
        
        extra_dirs.append(extra_dir)
        renamed_extra_dirs.append(rename_extra)
    
    root_dir.mkdir(exist_ok=True, parents=True)

    sampling = args.cluster_num
    if not sampling:
        sampling = int(input('Pls give max num of samples you want from each clusters: '))
    print('Max num of samples from each cluster:', sampling)

    sampled_count = 0

    if args.move: 
        shift_fn = move
    else:
        shift_fn = copy

    for cluster in clusters:
        if len(cluster) > sampling:
            sampled = random.sample(cluster, k=sampling)
        else:
            sampled = cluster
        
        for fn in sampled:
            src_path = orig_dir / fn
            shift_fn(str(src_path), str(root_dir))
            sampled_count += 1
            for extra_dst, extra_src, ext in zip(extra_dirs, renamed_extra_dirs, args.extra_ext): 
                extra_src_path = extra_src / f"{Path(fn).stem}.{ext}" 
                shift_fn(str(extra_src_path), str(extra_dst))

    print('Sampled total count: ', sampled_count)
    
    if args.move: 
        rmtree(orig_dir)
        for extra_src in renamed_extra_dirs:
            rmtree(extra_src)
