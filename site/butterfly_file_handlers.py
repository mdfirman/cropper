import yaml
import os
import operator
import glob
import collections


def extract_latin_name(name):
    if '(' in name:# and ')' in name:
        return name.split('(')[1].split(')')[0].strip().lower()
    else:
        return name.lower()


def build_unlabelled_img_set(data_dir, yaml_name):
    '''
    Returns set of unlabelled images, consisting of tuples of
    (sightingID, imageID)
    '''
    unlabelled_imgs = set()

    # yaml_paths = glob.glob(data_dir + '*/*meta.yaml')
    sighting_ids = yaml.load(
        open(data_dir + '../' + yaml_name), Loader=yaml.CLoader)

    for sighting_id, img_id, img_name in sighting_ids:

        # skip images with spaces, these are kind of broken
        if ' ' in img_id:
            continue

        meta = yaml.load(open(data_dir + sighting_id + '/meta.yaml'),
            Loader=yaml.CLoader)

        likely_id = extract_latin_name(meta['meta_tags']['likely_id'])

        # if likely_id != "pieris brassicae":
        #     continue

        crop_path = data_dir + sighting_id + '/' + img_id + '_crop.yaml'

        # could run glob.glob on data_dir just once to speed this up
        if not os.path.exists(crop_path):
            unlabelled_imgs.add((sighting_id, img_id, img_name))
        else:
            pass

    if len(unlabelled_imgs) == 0:
        print "No unlabelled images!"

    return unlabelled_imgs


def get_user_counts(data_dir):
    '''
    returns a list of users and an equivalent list of their counts,
    sorted so the most prolific users are last in the list
    '''
    uname_counts = collections.defaultdict(int)

    fnames = glob.glob(data_dir + '/*/*_crop.yaml')
    for fname in fnames:
        crop = yaml.load(open(fname))
        if 'username' in crop:
            uname_counts[crop['username']] += 1

    # sorting users
    sorted_users = sorted(uname_counts.items(), key=operator.itemgetter(1))
    return sorted_users
    #
    # unames, counts = zip(*sorted_users)
    # return unames, counts
