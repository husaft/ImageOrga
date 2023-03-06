import pickle
from os import walk
from os.path import join

import imagehash
import vptree
from PIL import Image

from utils_basic import write_file


def create_hashes(name, root, dicty, newly):
    i = 0
    for (dir_path, dir_names, file_names) in walk(root):
        for file_name in file_names:
            i = i + 1
            file_path = join(dir_path, file_name)
            if file_path in dicty:
                continue
            try:
                img = Image.open(file_path)
                h = img.height
                w = img.width
                fmt = img.format
                file_hash = str(imagehash.phash(img))
                print(f' [{i}] {file_path} ({w}x{h}, {fmt}) = {file_hash}')
                dicty[file_path] = {'w': w, 'h': h, 'f': fmt, 'x': file_hash}
                newly.append(file_path)
            except:
                print(f' * {file_path} is not an image!')
    write_file(name, dicty)


def hamming(a_str, b_str):
    a_hash = imagehash.hex_to_hash(a_str)
    b_hash = imagehash.hex_to_hash(b_str)
    return a_hash - b_hash


def calc_hashes(name, dest_dict, re_dict):
    hash_keys = set()
    for input_hash in dest_dict:
        hash_keys.add(input_hash)
    for input_hash in re_dict:
        hash_keys.add(input_hash)
    points = list(hash_keys)
    print(f"Storing {len(points)} hashes as tree...")
    tree = vptree.VPTree(points, hamming)
    with open(name, 'wb') as f:
        pickle.dump(tree, f)
    print(f"Finished the hash tree!")
    return tree
