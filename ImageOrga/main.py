from utils_defs import init_dict, load_tree, filter_only_exist
from utils_match import find_copies, match_exact, match_similar


def run_tool(repo, dest):
    print(f'Repo = {repo}')
    print(f'Dest = {dest}')

    re_dict_r, _, dest_dict_raw, new_files = init_dict(repo, dest, can_hash=True)
    find_copies(re_dict_r, dest_dict_raw, "dup", match_exact, None)
    ha_tree = load_tree(re_dict_r, dest_dict_raw)

    dest_dict_new = filter_only_exist(dest_dict_raw, lambda one_file: one_file in new_files)
    if len(dest_dict_new) >= 1:
        print(f"Searching for only {len(dest_dict_new)} of {len(dest_dict_raw)} hashes...")
        find_copies(re_dict_r, dest_dict_new, "sim", match_similar, {"dist": 10, "tree": ha_tree})

    print(f"Done.")


if __name__ == '__main__':
    run_tool('/data/sxnarod', '/data/sorted')
