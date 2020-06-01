import argparse
from tqdm import tqdm
from pathlib import Path

from imagededup.methods import PHash

# IMG_EXTS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
# IMG_EXTS = [ e.lower() for e in IMG_EXTS]
# IMG_EXTS.extend( [ e.upper() for e in IMG_EXTS ])

parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Path to root directory of images')
args = parser.parse_args()

root_dir = Path(args.directory)
assert root_dir.is_dir()

phasher = PHash()
# imgpaths = [p for p in root_dir.rglob('*') if p.suffix in IMG_EXTS ]
# encoding_map = {}
# for imgpath in tqdm(imgpaths):
# for imgpath in root_dir.rglob('*'):
    # if imgpath.suffix in IMG_EXTS:
        # encoding = phasher.encode_image(image_file=str(imgpath))
        # encoding_map[str(imgpath)] = encoding

encoding_map = phasher.encode_images(image_dir=root_dir, rglob=True)
dups = phasher.find_duplicates(encoding_map=encoding_map)

for main, ds in dups.items():
    if len(ds) > 0:
        print(main, ds)