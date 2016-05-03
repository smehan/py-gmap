# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-

# standard modules
import csv
import os
import pprint
import logging
import json
# 3rd party modules
from Gmap import map_api as goog
# Application modules
from loggerUtils import init_logging


def get_all_coords():
    data = {}
    with open("../data/input/nassau.txt") as infh:
        for line in infh:
            parts = line.split("\t")
            c = (parts[9], parts[10].strip())
            if parts[1] not in data:
                data[parts[1]] = c
        return(data)


def add_places(g, d, zip):
    """
    Go through results from google for a particular zip code, and format the result
    for entry into the dictionary
    :param g: google search results
    :param d: output dictionary
    :param zip: zip code for this particular search
    :return: d
    """
    for e in g:
        if e['name'] in d:
            continue
        else:
            d[e['name']] = [{'address': e['vicinity']},
                            {'plid': e['place_id']},
                            {'id': e['id']},
                            {'target-zip': zip}]
    return d


def reduce_coords(coords, zips=None):
    """
    Takes in the full set of coords by zip, and a
    list of zips to target and outputs
    the reduced set of coords by zip.
    :type zips: list
    :param coords: dictionary of {zip: (lat, long)}
    :param zips: list of [zips] that should be targeted. If none supplied is None
    :return: a reduced dictionary of {zip:(lat, long)}
    """
    if not zips:  # nothing supplied to reduce, so return full input
        return coords
    return {z: coords.get(z, None) for z in zips}


def output_data(data, path, use_json=False, method='radar'):
    names = ('target-zip', 'name', 'address', 'plid', 'id')
    if method == 'radar':  # TODO: slim support for radar, so needs to dump json
        #use_json = True
        pass
    if use_json is True:
        with open(path, 'w') as fh:
            json.dump(data, fh)
    elif not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as fh:
            outwriter = csv.DictWriter(fh, fieldnames=names, delimiter='\t')
            outwriter.writeheader()
    else:
        with open(path, 'a') as fh:
            outwriter = csv.writer(fh, delimiter='\t')
            for name in data:
                outwriter.writerow([data[name][3]['target-zip'], name, data[name][0]['address'], data[name][1]['plid'], data[name][2]['id']])

if __name__ == '__main__':
    path = "../data/output/search-20160503.csv"
    # these lists are from model.py output, ranked on that feature
    # currently set up to only use one as param in reduce_coords
    top_pop = ['11550','11561','11520','11542','11590','11050','11580','11003','11801','11021']
    top_renter_den = ['11096', '11022', '11550', '11571', '11551', '11542', '11561', '11516', '11582', '11549']
    extract = goog.Gmap()  # build a gmap object to handle interface with google maps api.
    coord_dict = get_all_coords()
    pop_coords = reduce_coords(coord_dict, top_renter_den)
    places = {}
    for k in pop_coords:
        result = []
        coords = pop_coords[k]
        result, search_type = extract.fetch_results(coords, rad=5000, place_type='laundry', keywords=('laundromat'))
        if search_type == 'nearby':
            places = add_places(result, places, k)
    pprint.pprint(places)
    output_data(places, path)
    print("********************Job Finished************************************")