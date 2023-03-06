from os.path import isfile, join, isdir, basename
from os import mkdir, rename
import pickle
import numpy as np
from multiprocessing import Pool
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.preprocessing.image import image_utils
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from utils_defs import init_dict


def extract_features(file, model):
    raw_img = image_utils.load_img(file, target_size=(224, 224))
    img = np.array(raw_img)
    reshaped_img = img.reshape(1, 224, 224, 3)
    imgx = preprocess_input(reshaped_img)
    features = model.predict(imgx, use_multiprocessing=True)
    return features


def find_all_files(re_dict):
    all_files = list()
    for one_key in re_dict:
        one_val = re_dict[one_key]
        for one_file in one_val:
            one_file_name = one_file["n"]
            if not isfile(one_file_name):
                continue
            all_files.append(one_file_name)
    return all_files


def init_f_dict(files_list, can_feat):
    new_file_names = list()

    ft_name = 'feat-dict.pickle'
    feat_dict = dict()
    if isfile(ft_name):
        with open(ft_name, 'rb') as f:
            feat_dict = pickle.load(f)
    if can_feat:
        model = VGG16()
        model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
        create_features(ft_name, files_list, feat_dict, new_file_names, model)

    return feat_dict, new_file_names


def create_features(name, file_list, dicty, newly, model):
    i = 0
    for file_path in file_list:
        i = i + 1
        if file_path in dicty:
            continue
        try:
            feat = extract_features(file_path, model)
            print(f' [{i}] {file_path} = {feat}')
            dicty[file_path] = feat
            newly.append(file_path)
        except:
            print(f' * {file_path} is not an image!')
    with open(name, 'wb') as f:
        pickle.dump(dicty, f)


def fit_kmeans(arg):
    k, x = arg
    kmeans = KMeans(n_clusters=k, random_state=22, n_init="auto").fit(x)
    labels = kmeans.labels_
    res = k, silhouette_score(x, labels, metric='euclidean')
    print(f" - Cluster size of {res[0]} results in {res[1]} ...")
    return res


def run_tool(repo, dest):
    print(f'Repo = {repo}')
    print(f'Dest = {dest}')

    re_dict_r, _, dest_dict_raw, new_files = init_dict(repo, dest, can_hash=True)
    files = find_all_files(re_dict_r)
    feat_dict, _ = init_f_dict(files, can_feat=True)

    filenames = np.array(list(feat_dict.keys()))
    feat = np.array(list(feat_dict.values()))
    feat = feat.reshape(-1, 4096)

    pca = PCA(n_components=100, random_state=22)
    pca.fit(feat)
    x = pca.transform(feat)

    kbeg = 120
    kend = kbeg + 30
    krng = range(kbeg, kend + 1)

    with Pool() as pool:
        items = [(pi, x) for pi in krng]
        sil = pool.map(fit_kmeans, items)

    silm = sorted(sil, key=lambda y: y[1], reverse=True)
    silm_win = silm[0]
    num_k = silm_win[0]
    silm_itm_count = round((len(filenames) * 1.0) / num_k)

    kmeans = KMeans(n_clusters=num_k, random_state=22, n_init='auto')
    kmeans.fit(x)

    groups = {}
    for file, cluster in zip(filenames, kmeans.labels_):
        if cluster not in groups.keys():
            groups[cluster] = []
            groups[cluster].append(file)
        else:
            groups[cluster].append(file)

    cluster_dir = join(repo, 'cluster')
    if not isdir(cluster_dir):
        mkdir(cluster_dir)

    len_all = list()
    for one_group in sorted(groups.keys()):
        one_values = groups[one_group]
        len_all.append(len(one_values))

        cluster_sub_dir = join(cluster_dir, f"k{one_group:04d}")
        cluster_sub_name = basename(cluster_sub_dir)[1:]
        if not isdir(cluster_sub_dir):
            mkdir(cluster_sub_dir)

        for one_file in sorted(one_values):
            cluster_file_name = basename(one_file)
            cluster_sub_file = join(cluster_sub_dir, cluster_file_name)
            if isfile(cluster_sub_file):
                continue

            print(f' [{cluster_sub_name}] {one_file}')
            print(f'       --> {cluster_sub_file}')
            rename(one_file, cluster_sub_file)

    len_all = sorted(len_all)
    print(f"Files count = {len(files)}")
    print(f"Recommended cluster = {silm_win}")
    print(f"Average items per cluster = {silm_itm_count}")
    print(f"Minimum files per cluster = {len_all[0]}")
    print(f"Maximum files per cluster = {len_all[-1]}")


if __name__ == '__main__':
    run_tool('/data/all', '/data/sorted')
