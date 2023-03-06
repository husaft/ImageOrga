from datetime import datetime
from os import stat, rename, mkdir
from os.path import basename, splitext, isfile, join, dirname, isdir
from humanize import naturalsize, intword
from utils_defs import init_dict, group_by_folder_and_hash, filter_only_exist


def to_date_str(ts):
    tsd = datetime.fromtimestamp(ts)
    return tsd.strftime("%Y/%m/%d %H:%M:%S")


def read_file(val_file):
    item_fmt = val_file['f']
    item_fil = val_file['n']
    stinfo = stat(item_fil)

    t_modtime = stinfo.st_mtime
    t_mettime = stinfo.st_ctime
    mod_time = max(t_modtime, t_mettime)

    t_size = stinfo.st_size
    item_w = val_file['w']
    item_h = val_file['h']
    item_reso = item_w * item_h

    return item_fil, item_fmt, t_size, item_reso, mod_time, (item_w, item_h)


def run_tool(repo, dest):
    print(f'Repo = {repo}')
    print(f'Dest = {dest}')

    lq_folder_name = "low"
    lq_filter = lambda file_name: basename(dirname(file_name)) != lq_folder_name

    re_dict_r, _, dest_dict_r, _ = init_dict(repo, dest, can_hash=True)
    dest_dict_r = filter_only_exist(dest_dict_r, lq_filter)

    dest_dict_wrg, dest_dict_grp = group_by_folder_and_hash(dest_dict_r)
    dest_dict_wrg_norm = [x for x in dest_dict_wrg.keys()]
    wrong_hash_count = len(dest_dict_wrg_norm)
    if wrong_hash_count >= 1:
        print(f"{wrong_hash_count} doubled files in different folders!")
        return

    print(f"Found {len(dest_dict_grp)} folders:")
    for folder_name in dest_dict_grp:
        folder_short = basename(folder_name)
        if folder_short == lq_folder_name:
            continue

        folder_val = dest_dict_grp[folder_name]
        folder_hash_count = len(folder_val)
        folder_all_count = sum([len(folder_val[x]) for x in folder_val])
        print(f" - {folder_name} ({folder_hash_count} / {folder_all_count})")

        for folder_val_key in folder_val:
            print(f"    - {folder_val_key}")

            folder_items_raw = [read_file(x) for x in folder_val[folder_val_key]]
            folder_items_sized = sorted(folder_items_raw, key=lambda x: (x[3], x[2]), reverse=True)

            i = 0
            for (i_name, i_fmt, i_size, i_resu, i_mod, i_wh) in folder_items_sized:
                i += 1
                l_name = basename(i_name)
                l_size = naturalsize(i_size)
                l_resu = intword(i_resu)
                l_time = to_date_str(i_mod)
                (item_w, item_h) = i_wh
                print(f"       [{i}] {l_name}, {item_w}x{item_h}, "
                      f"{l_size}, {i_fmt}, {l_resu} px, {l_time}")

                tmp_ext = splitext(i_name)
                tmp_f = tmp_ext[0]
                tmp_e = tmp_ext[1]
                tmp_ff = '.' + i_fmt.lower()
                if tmp_ff != tmp_e:
                    tmp_old_name = i_name
                    tmp_new_name = tmp_f + tmp_ff
                    if not isfile(tmp_new_name):
                        rename(tmp_old_name, tmp_new_name)
                        i_name = tmp_new_name

                if i >= 2:
                    lq_file_dir = dirname(i_name)
                    lq_folder = join(lq_file_dir, lq_folder_name)
                    if not isdir(lq_folder):
                        mkdir(lq_folder)
                    lq_file_name = basename(i_name)
                    lq_full_name = join(lq_folder, lq_file_name)
                    if not isfile(lq_full_name):
                        rename(i_name, lq_full_name)


if __name__ == '__main__':
    run_tool('/data/all', '/data/sorted')
