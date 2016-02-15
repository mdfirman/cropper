import yaml
import os
import operator
import glob
import time
import collections
import socket

num_labellers_required_per_image = 3


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
    tic = time.time()
    unlabelled_imgs = set()

    # keys are (sighting_id, img_id) tuples
    # values are a dict containing:
        # image name
        # a list of who has labelled which images
    # ultimately make this an ordered dict we can pop items off...
    who_labelled_what = collections.OrderedDict()

    # find names of all the images in the collection
    sighting_ids = yaml.load(
        open(data_dir + '../' + yaml_name), Loader=yaml.CLoader)

    for sighting_id, img_id, img_name in sighting_ids:

        # skip images with spaces, these are kind of broken
        if ' ' in img_id:
            continue

        who_labelled_what[(sighting_id, img_id)] = {
            'img_name': img_name, 'labellers': set()}

    # finding the croppings which have been already performed
    start = len(data_dir)
    crop_paths = glob.glob(data_dir + '*/*_crop.yaml')

    for crop_path in crop_paths:
        sighting_id, tmp = crop_path[start:].split('/')
        splitup = tmp.split('_')
        user = splitup[-2]
        img_id = '_'.join(splitup[:-2])
        who_labelled_what[(sighting_id, img_id)]['labellers'].add(user)

    # sort the dictionary by how many times each item has been labelled
    who_labelled_what = collections.OrderedDict(sorted(
        who_labelled_what.items(),
        key=lambda x: len(x[1]['labellers']), reverse=True))

    # remove items from the dict which have been done enough times
    who_labelled_what = collections.OrderedDict(
        (xx, yy) for xx, yy in who_labelled_what.items()
        if len(yy['labellers']) < num_labellers_required_per_image
    )

    # this orderddict is now the main dictionary.
    # when a user makes a request for a new item to label, we iterate through
    # the dictionary from least to most labelled until we find an item they
    # haven't labelled

    # when the set of users who have labelled each item gets big enough, we
    # remove it from the list

    # this will be slower now for users who have labelled many items, but
    # in a typical use case I imagine most users will have labelled < 500
    # so shouldn't be too bad

    # todo - after user submits, we need to add their name to the set and remove if needed

    print yaml.dump(who_labelled_what)

    if len(who_labelled_what) == 0:
        print "No unlabelled images!"

    print "Took %fs to build unlabelled image set" % (time.time() - tic)

    return who_labelled_what


def get_user_counts(data_dir):
    '''
    returns a list of users and an equivalent list of their counts,
    sorted so the most prolific users are last in the list
    '''
    tic = time.time()
    uname_counts = collections.defaultdict(int)

    fnames = glob.glob(data_dir + '/*/*_crop.yaml')
    start = len(data_dir)
    for fname in fnames:
        username = fname[start:].split('_')[-2]
        print 'Username', username
        uname_counts[username] += 1

    # sorting users
    sorted_users = sorted(uname_counts.items(), key=operator.itemgetter(1))

    print "Getting user counts took %fs" % (time.time() - tic)
    return sorted_users


def getpaths(debug):

    host = socket.gethostname()

    if host == 'biryani':
        if debug:
            data_dir = '/media/michael/Engage/data/butterflies/web_scraping/ispot/sightings_tmp_for_beta/'
            yaml_name = 'butterflies_for_beta_website.yaml'
        else:
            data_dir = '/media/michael/Engage/data/butterflies/web_scraping/ispot/butterfly_subset/'
            yaml_name = 'butterflies.yaml'

    elif host == 'oisin':
        if debug:
            data_dir = '/home/admin/butterflies/data/sightings/'
            yaml_name = 'butterflies_for_beta_website.yaml'
        else:
            raise Exception('Not ready for the real thing yet')
    else:
        raise Exception("Unknown host, expected 'oisin' or 'biryani'")

    return data_dir, yaml_name
