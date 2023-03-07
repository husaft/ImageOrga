from functools import cmp_to_key
from os.path import basename, dirname, getsize
from os import stat, utime
from datetime import datetime
from utils_defs import init_dict, filter_only_exist, group_by_folder_and_hash
from utils_hash import hamming

sizes = dict()


def compare_hash_file(a, b):
    res = hamming(a, b)
    diff = sizes[b] - sizes[a]
    res = res if diff >= 0 else -res
    res = res + (diff / 100000.0)
    return res


def order_folder(folder, content):
    print(f' * {folder}')

    hash_keys = set()
    for input_hash in content:
        hash_keys.add(input_hash)

    points_list = sorted(hash_keys)
    times = dict()
    i = 0

    while len(points_list) >= 1:
        i += 1
        current_hash = points_list.pop()
        current_file = content[current_hash][0]['n']
        current_name = basename(current_file)

        nat_size = getsize(current_file)
        sizes[current_hash] = nat_size

        current_stat = stat(current_file)
        mod_time = current_stat.st_mtime
        times[current_hash] = mod_time

        mod_time_obj = datetime.fromtimestamp(mod_time)
        date_obj = mod_time_obj.strftime('%Y-%m-%d %H:%M:%S')
        print(f"    [{i}] ({current_hash.upper()}) '{current_name}', modified at {date_obj}")

    new_time = None
    points_copy = sorted(hash_keys, key=cmp_to_key(compare_hash_file))
    for points_item in points_copy:
        con_time = times[points_item]
        if new_time is None:
            new_time = con_time
            continue
        new_time += 1
        con_file = content[points_item][0]['n']
        utime(con_file, (new_time, new_time))


def run_tool(repo):
    print(f'Repo = {repo}')

    lq_folder_name = "low"
    lq_filter = lambda file_name: basename(dirname(file_name)) != lq_folder_name

    re_dict_r, _, _, _ = init_dict(repo, repo, can_hash=True)
    repo_dict_r = filter_only_exist(re_dict_r, lq_filter)

    repo_dict_wrg, repo_dict_grp = group_by_folder_and_hash(repo_dict_r)
    wrong_hash_count = len(repo_dict_wrg.keys())
    if wrong_hash_count >= 1:
        print(f"{wrong_hash_count} doubled files in different folders!")
        return

    print(f"Found {len(repo_dict_grp)} folders...")

    for folder_name in repo_dict_grp:
        folder_short = basename(folder_name)
        if folder_short == lq_folder_name:
            continue
        order_folder(folder_name, repo_dict_grp[folder_name])

    print(f"Done.")


if __name__ == '__main__':
    run_tool('/data/all')
