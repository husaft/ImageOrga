from multiprocessing import Pool
from os import mkdir, rename
from os.path import join, isfile, isdir, basename, dirname, splitext


def match_exact(one_hash, all_dict, _):
    if one_hash in all_dict:
        return [(0, one_hash)]
    else:
        return []


def match_similar(one_hash, all_dict, opt):
    h_tree = opt["tree"]
    h_dist = opt["dist"]
    # Looking for {one_hash} with distance of {h_dist}...
    results = h_tree.get_all_in_range(one_hash, h_dist)
    return [x for x in results if x[0] >= 1 and x[1] in all_dict]


def find_copy(arg):
    one_hash = arg[0]
    done_dict = arg[1]
    sub_fld = arg[2]
    i = arg[3]
    match = arg[4]
    all_dict = arg[5]
    opt = arg[6]

    one_val = done_dict[one_hash]
    one_dir = set([dirname(x["n"]) for x in one_val]).pop()
    dup_dir = join(one_dir, sub_fld)

    tmp = list()
    for (item_dist, item_hash) in match(one_hash, all_dict, opt):
        for all_val in all_dict[item_hash]:
            all_file = all_val["n"]
            if not isfile(all_file):
                continue
            all_fmt = all_val["f"].lower()
            all_name = splitext(basename(all_file))[0] + "." + all_fmt
            all_new = join(dup_dir, all_name)
            if isfile(all_new):
                print(f' * {all_new} already exists!')
                continue
            tmp.append((all_file, item_dist, all_new, i))
    return tmp


def find_copies(all_dict, done_dict, sub_fld, match, opt):
    with Pool() as pool:
        items = [(t, done_dict, sub_fld, i, match, all_dict, opt) for i, t in enumerate(done_dict.keys())]
        raw_collected = pool.map(find_copy, items)
        flat_collected = [x for y in raw_collected for x in y]
        tmp_collected = dict()
        for one_item in flat_collected:
            one_key = one_item[0]
            one_list = list()
            if one_key in tmp_collected:
                one_list = tmp_collected[one_key]
            else:
                tmp_collected[one_key] = one_list
            one_list.append(one_item)
        for file_name in sorted(tmp_collected.keys()):
            res = sorted(tmp_collected[file_name], key=lambda y: y[1])
            first = res[0]
            all_file = first[0]
            all_new = first[2]
            if not isfile(all_file):
                continue
            tgt_dir = dirname(all_new)
            if not isdir(tgt_dir):
                mkdir(tgt_dir)
            all_dist = first[1]
            i = first[3]
            print(f' [{i}] {all_file} with dist {all_dist}')
            print(f'       --> {all_new}')
            rename(all_file, all_new)
