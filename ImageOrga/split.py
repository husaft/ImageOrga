import os
from collections import defaultdict
from os.path import isfile, isdir, basename, dirname
import humanize
from utils_defs import init_dict


def get_stats(dest_dict):
    i = 0
    formats = set()
    sizes = set()
    pixels = set()
    fbytes = set()
    for key in dest_dict:
        val = dest_dict[key]
        for sub_val in val:
            fn = sub_val["n"]
            if not os.path.isfile(fn):
                continue
            i = i + 1
            fmt = str(sub_val["f"])
            fh = sub_val["h"]
            fw = sub_val["w"]
            fm = fh * fw
            fs = (fm, f"{fh}x{fw}")
            fbs = os.path.getsize(fn)
            fb = humanize.naturalsize(fbs)
            formats.add(fmt)
            sizes.add(fs)
            pixels.add(fm)
            fbytes.add((fbs, fb))
    all_formats = list(sorted(formats))
    all_fbytes = [x[1] for x in list(sorted(fbytes))]
    all_pixels = list(sorted(pixels))
    all_sizes = [x[1] for x in list(sorted(sizes))]
    return i, all_formats, all_fbytes, all_pixels, all_sizes


def split_files(repo_dict, min_pix, max_pix, all_fmts, all_pix, all_sizes, all_fbytes):
    i = 0
    found = list()
    for key in repo_dict:
        val = repo_dict[key]
        for sub_val in val:
            fn = sub_val["n"]
            if not os.path.isfile(fn):
                continue
            i = i + 1
            fmt = str(sub_val["f"])
            fh = sub_val["h"]
            fw = sub_val["w"]
            fm = fh * fw
            fs = f"{fh}x{fw}"
            fbs = os.path.getsize(fn)
            fb = humanize.naturalsize(fbs)
            cat = []
            if fmt in all_fmts:
                cat.append("fmt-good")
            else:
                cat.append("fmt-fail")
            if fb in all_fbytes:
                cat.append("byt-good")
            else:
                cat.append("byt-fail")
            if fs in all_sizes:
                cat.append("siz-good")
            else:
                cat.append("siz-fail")
            if fm < min_pix:
                cat.append("pix-small")
            elif fm > max_pix:
                cat.append("pix-big")
            elif fm in all_pix:
                cat.append("pix-good")
            else:
                cat.append("pix-maybe")
            found.append((fn, cat))
    return i, found


def run_tool(repo, dest):
    print(f'Repo = {repo}')
    print(f'Dest = {dest}')

    re_dict_r, re_dict, dest_dict_r = init_dict(repo, dest)
    files_count, formats, fbytes, pixels, sizes = get_stats(dest_dict_r)

    min_pixels = pixels[0]
    max_pixels = pixels[len(pixels) - 1]
    min_sizes = sizes[0]
    max_sizes = sizes[len(sizes) - 1]
    min_fbytes = fbytes[0]
    max_fbytes = fbytes[len(fbytes) - 1]
    print(f"Sorted files")
    print(f"   count   = {files_count}")
    print(f"   formats = {formats}")
    print(f"   pixels  = {min_pixels} - {max_pixels}")
    print(f"   sizes   = {min_sizes} - {max_sizes}")
    print(f"   bytes   = {min_fbytes} - {max_fbytes}")

    r_files_count, cat_files = split_files(re_dict_r, min_pixels, max_pixels, formats, pixels, sizes, fbytes)
    cat_dict = defaultdict(list)
    for v, k in [(n, '_'.join(c)) for (n, c) in cat_files]:
        cat_dict[k].append(v)
    print(f"Unknown files")
    print(f"   count (all)   = {r_files_count}")
    i = 0
    for one_cat in sorted(cat_dict.keys()):
        one_items = cat_dict[one_cat]
        print(f"   count ({one_cat}) = {len(one_items)}")
        spl_dir = os.path.join(repo, one_cat)
        for one_file in one_items:
            if not isfile(one_file):
                continue
            i = i + 1
            all_val = re_dict[one_file]
            all_fmt = all_val["f"].lower()
            all_name = os.path.splitext(basename(one_file))[0] + "." + all_fmt
            all_new = os.path.join(spl_dir, all_name)
            if isfile(all_new):
                print(f' * {all_new} already exists!')
                continue
            tgt_dir = dirname(all_new)
            if not isdir(tgt_dir):
                os.mkdir(tgt_dir)
            print(f' [{i}] {one_file}')
            print(f'       --> {all_new}')
            os.rename(one_file, all_new)


if __name__ == '__main__':
    run_tool('/data/all', '/data/sorted')
