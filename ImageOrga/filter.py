import humanize
import os.path
import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf
from os.path import basename, dirname
from utils_defs import init_dict, filter_only_exist
from utils_match import find_copy, match_exact


def find_simple(term_hash, done_dict, i, all_dict):
    res = find_copy((term_hash, done_dict, "xyz", i, match_exact, all_dict, None))
    like_dirs = set()
    for item in res:
        like_item = item[0]
        like_dir = os.path.dirname(like_item)
        like_dirs.add(like_dir)
    like_dirs_names = [os.path.basename(x) for x in sorted(like_dirs)]
    return like_dirs_names


class ImgWindow(Gtk.Window):
    def __init__(self, repo, dest):
        super().__init__(title="Image Viewer")

        print(f'Repo = {repo}')
        print(f'Dest = {dest}')
        self.dest_fld = dest
        self.re_dict_r, _, self.dest_dict_r = init_dict(repo, dest)

        lq_folder_name = "low"
        lq_filter = lambda file_name: basename(dirname(file_name)) != lq_folder_name
        self.re_dict_r = filter_only_exist(self.re_dict_r, lq_filter)
        self.dest_dict_r = filter_only_exist(self.dest_dict_r, lq_filter)

        self.t_w = 800
        self.t_h = 800

        self.image_frame = Gtk.Frame()
        self.image_frame.set_label("...")
        self.image = Gtk.Image()
        self.image_frame.add(self.image)

        self.image_detail = Gtk.Label()
        self.image_detail.set_text("...")

        self.skip_btn = Gtk.Button(label="Skip")
        self.skip_btn.connect("clicked", self.on_skip_btn_clicked)

        self.radio_grp1 = Gtk.TextView()
        self.radio_grp1.set_editable(False)
        self.radio_grp1.set_wrap_mode(Gtk.WrapMode.WORD)

        self.stack_top = Gtk.Grid()
        self.stack_top.attach(self.image_frame, 0, 0, 1, 1)
        self.stack_top.attach_next_to(self.image_detail, self.image_frame, Gtk.PositionType.BOTTOM, 1, 1)
        self.stack_top.attach_next_to(self.skip_btn, self.image_detail, Gtk.PositionType.BOTTOM, 1, 1)
        self.stack_top.attach_next_to(self.radio_grp1, self.skip_btn, Gtk.PositionType.BOTTOM, 1, 1)
        self.add(self.stack_top)

        self.last_keys = list()
        self.connect("key-release-event", self.process_key)

        self.re_dict_keys = list(sorted(self.re_dict_r.keys()))
        self.re_dict_index = 0
        self.re_dict_count = len(self.re_dict_keys)
        self.next_image()

    def process_key(self, _, e):
        sign = e.string
        if sign == '-':
            self.last_keys = ['0', '3']
        elif sign == '+':
            self.last_keys = ['0', '2']
        elif sign == '*':
            self.last_keys = ['0', '1']
        else:
            self.last_keys.append(sign)
        if len(self.last_keys) < 2:
            return
        sign_cmd = "".join(self.last_keys)
        self.last_keys.clear()
        id_cmd = self.id_dict[sign_cmd]
        from_file = self.current_file
        dir1 = os.path.join(self.dest_fld, id_cmd)
        if not os.path.isdir(dir1):
            os.mkdir(dir1)
        dir2 = os.path.join(dir1, 'sim')
        if not os.path.isdir(dir2):
            os.mkdir(dir2)
        to_file = os.path.join(dir2, os.path.basename(from_file))
        i = self.re_dict_index
        print(f' [{i}] {from_file}')
        print(f'       --> {to_file}')
        os.rename(from_file, to_file)
        self.next_image()

    def change_image(self, file_name):
        pix_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=file_name,
            width=self.t_w, height=self.t_h,
            preserve_aspect_ratio=True)
        self.image.set_from_pixbuf(pix_buf)
        self.image_frame.set_label(f" [{self.re_dict_index} / {self.re_dict_count}] {file_name}")

    def change_detail(self):
        curr_hash = self.current_item["x"].upper()
        curr_fmt = self.current_item["f"]
        curr_w = self.current_item["w"]
        curr_h = self.current_item["h"]
        curr_len = len(self.current_items)
        curr_fn = self.current_item["n"]
        fb = humanize.naturalsize(os.path.getsize(curr_fn))
        txt = f"{curr_hash}, {curr_w}x{curr_h}, {curr_fmt}, {fb}, {curr_len} item(s)"
        self.image_detail.set_text(txt)

    def change_radio(self, like_dirs):
        res = dict()
        lines1 = list()
        lines2 = list()
        lines2.append("___________________________________")
        i = 0
        for like_dir in like_dirs:
            i = i + 1
            id = '{:0>2}'.format(i)
            name = f"({id}) {like_dir}"
            res[id] = like_dir
            if i > 56:
                lines2.append(name)
            else:
                lines1.append(name)

        txt1 = " ".join(lines1)
        buff1 = Gtk.TextBuffer()
        buff1.set_text(txt1)
        self.radio_grp1.set_buffer(buff1)
        return res

    def next_image(self):
        if len(self.re_dict_keys) < 1:
            self.close()
            return
        self.current_hash = self.re_dict_keys.pop()
        self.re_dict_index = self.re_dict_index + 1
        self.current_items = self.re_dict_r[self.current_hash]
        self.current_item = self.current_items[0]
        self.current_file = self.current_item["n"]
        self.change_image(self.current_file)
        self.change_detail()
        like_dirs = find_simple(self.current_item["x"], self.re_dict_r,
                                self.re_dict_index, self.dest_dict_r)
        like_dirs.insert(0, "trash")
        like_dirs.insert(0, "keep")
        like_dirs.insert(0, "later")
        self.id_dict = self.change_radio(like_dirs)

    def on_skip_btn_clicked(self, _):
        self.next_image()


def run_tool(repo, dest):
    win = ImgWindow(repo, dest)
    win.connect("destroy", Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    run_tool('/data/all', '/data/sorted')
