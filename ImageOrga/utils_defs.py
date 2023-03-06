import pickle
from os.path import isfile, dirname
from utils_basic import read_file, reverse_dict
from utils_hash import calc_hashes
from utils_hash import create_hashes


def init_dict(repo, dest, can_hash):
    new_file_names = list()

    dd_name = 'dest-dict.json'
    dest_dict = dict()
    if isfile(dd_name):
        dest_dict = read_file(dd_name)
    if can_hash:
        create_hashes(dd_name, dest, dest_dict, new_file_names)

    re_name = 'repo-dict.json'
    re_dict = dict()
    if isfile(re_name):
        re_dict = read_file(re_name)
    if can_hash:
        create_hashes(re_name, repo, re_dict, list())

    re_dict_r = reverse_dict(re_dict)
    dest_dict_r = reverse_dict(dest_dict)

    return re_dict_r, re_dict, dest_dict_r, new_file_names


def load_tree(re_dict_r, dest_dict_r):
    ha_name = 'hash-tree.pickle'
    if isfile(ha_name):
        with open(ha_name, 'rb') as f:
            ha_tree = pickle.load(f)
    else:
        ha_tree = calc_hashes(ha_name, dest_dict_r, re_dict_r)
    return ha_tree


def filter_only_list(dicty, allowed_keys):
    res = dict()
    for one_key in dicty:
        if one_key in allowed_keys:
            res[one_key] = dicty[one_key]
    return res


def filter_only_exist(dicty, is_good):
    res = dict()
    for one_hash in dicty:
        val = [x for x in dicty[one_hash] if isfile(x["n"]) and is_good(x["n"])]
        if len(val) >= 1:
            res[one_hash] = val
    return res


def group_by_folder_and_hash(dest_dict):
    wrong = dict()
    right = dict()

    for one_hash in dest_dict:
        one_val = dest_dict[one_hash]
        one_dirs = list(set([dirname(x["n"]) for x in one_val]))
        if len(one_dirs) >= 2:
            wrong[one_hash] = one_val
            continue

        one_folder = one_dirs[0]
        one_list = dict()
        if one_folder in right:
            one_list = right[one_folder]
        else:
            right[one_folder] = one_list

        for one_item in one_val:
            this_hash = one_item['x']
            this_list = list()
            if this_hash in one_list:
                this_list = one_list[this_hash]
            else:
                one_list[this_hash] = this_list
            this_list.append(one_item)

    return wrong, right
