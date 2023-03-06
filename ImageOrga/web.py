from random import shuffle
from yattag import Doc
from flask import Flask, send_file
from os.path import basename, dirname
from utils_defs import init_dict, filter_only_exist, group_by_folder_and_hash


def generate_file_read(sub_path):
    sub_path = '/' + sub_path
    return send_file(sub_path, mimetype='image/webp')


def generate_folder_view(dest_dict_df, dest_dict_of, pix_count):
    title_txt = 'Images Overview'

    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')

    with tag('html'):
        with tag('head'):
            line('title', title_txt)

        with tag('body'):
            line('h1', title_txt)

            if len(dest_dict_df) >= 1:
                with tag('div'):
                    line('h2', 'Different folder detection:')
                    with tag('table', border=1):
                        with tag('thead'):
                            with tag('tr'):
                                for j in ["Hash", "File", "Width", "Height", "Format"]:
                                    line('th', j)
                        with tag('tbody'):
                            for key in dest_dict_df:
                                val = dest_dict_df[key]
                                with tag('tr'):
                                    line('td', key)
                                    line('td', '')
                                    line('td', '')
                                    line('td', '')
                                    line('td', '')
                                for j in val:
                                    file_name = j['n']
                                    with tag('tr'):
                                        line('td', '')
                                        with tag('td'):
                                            with tag('a', href=f"raw/{file_name}"):
                                                text(file_name)
                                        line('td', j['w'])
                                        line('td', j['h'])
                                        line('td', j['f'])

            if len(dest_dict_of) >= 1:
                with tag('div'):
                    line('h2', 'All folder contents:')
                    with tag('table', border=1):
                        with tag('thead'):
                            text('')
                        with tag('tbody'):
                            for folder_name in sorted(dest_dict_of.keys()):
                                hash_dict = dest_dict_of[folder_name]
                                hashes = [x for x in hash_dict.keys()]
                                length = [len(hash_dict[x]) for x in hashes]
                                shuffle(hashes)
                                with tag('tr'):
                                    line('td', basename(folder_name))
                                    line('td', f"{len(hash_dict)} / {sum(length)}")
                                    size = "96"
                                    with tag('td'):
                                        i = 0
                                        for my_hash in hashes:
                                            i = i + 1
                                            o = hash_dict[my_hash][0]
                                            file_name = o['n']
                                            with tag('img', width=size, height=size, src=f"raw/{file_name}",
                                                     style='object-fit: contain;'):
                                                text('')
                                            if i >= pix_count:
                                                break

    return doc.getvalue()


def low_filter(file_name):
    short = basename(dirname(file_name))
    return short not in ["low", "dup", "sim"]


def run_tool(repo, dest):
    app = Flask(__name__)

    @app.route("/")
    def show_folder_view_std():
        return show_folder_view(8)

    @app.route("/folders/<int:limit>")
    def show_folder_view(limit):
        print(f'Repo = {repo}')
        print(f'Dest = {dest}')
        re_dict_r, _, dest_dict_r, _ = init_dict(repo, dest, can_hash=False)
        dest_dict_r = filter_only_exist(dest_dict_r, low_filter)
        dest_dict_w, dest_dict_g = group_by_folder_and_hash(dest_dict_r)
        return generate_folder_view(dest_dict_w, dest_dict_g, limit)

    @app.route("/raw/<path:subpath>")
    def show_raw_file_std(subpath):
        return generate_file_read(subpath)

    @app.route("/folders/raw/<path:subpath>")
    def show_raw_file(subpath):
        return generate_file_read(subpath)

    app.run()


if __name__ == '__main__':
    run_tool('/data/all', '/data/sorted')
