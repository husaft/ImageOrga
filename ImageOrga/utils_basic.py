import json


def read_file(name):
    with open(name, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_file(name, dicty):
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(dicty, f, ensure_ascii=False, indent=4, sort_keys=True)


def reverse_dict(dicty):
    res = dict()
    for key in dicty:
        val = dicty[key]
        v_hash = val["x"]
        val["n"] = key
        if v_hash in res:
            e_list = res[v_hash]
            e_list.append(val)
        else:
            n_list = list()
            n_list.append(val)
            res[v_hash] = n_list
    return res
