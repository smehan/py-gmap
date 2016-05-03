# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-
import csv
import os
import pprint

def read_places(path):
    with open(path, 'r') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        return {r['name']: r for r in reader}


def read_model(path):
    output = []
    with open(path, 'r') as fh:
        reader = csv.reader(fh)
        for r in reader:
            output.append(r)
        return output


def sift_results(places, model):
    freq = {}
    m = get_model_dict(model)
    for k,v in places.items():
        places[k]['avg_renter_density'] = m[places[k]['target-zip']]['avg_renter_density']
        places[k]['avg_renter_income'] = m[places[k]['target-zip']]['avg_renter_income']
        places[k]['renter_pop_est'] = m[places[k]['target-zip']]['renter_pop_est']
        if freq.get(places[k]['target-zip']):
            freq[places[k]['target-zip']] += 1
        else:
            freq[places[k]['target-zip']] = 1
    pprint.pprint(freq)
    return(places)

def get_model_dict(model):
    model_dict = {}
    for r in model:
        model_dict[r[0]] = {'avg_renter_density': r[1],
                            'max_renter_density': r[2],
                            'avg_renter_income': r[3],
                            'max_renter_income': r[4],
                            'avg_h1_renter_density': r[5],
                            'max_h1_renter_density': r[6],
                            'avg_h2_renter_density': r[7],
                            'max_h2_renter_density': r[8],
                            'avg_h3_renter_density': r[9],
                            'max_h3_renter_density': r[10],
                            'avg_h4_renter_density': r[11],
                            'max_h4_renter_density': r[12],
                            'renter_pop_est': r[13]}
    return model_dict


def write_output(d, path):
    with open(path, 'w', encoding='utf-8') as fh:
        fieldnames = ["target-zip", "name","address","avg_renter_density","avg_renter_income","id","plid","renter_pop_est"]
        writer = csv.DictWriter(fh, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        for r in d:
            writer.writerow(d[r])

if __name__ == '__main__':
    places = read_places("../data/output/search-20160415.csv")
    model = read_model("../data/output/model.csv")
    output = sift_results(places, model)
    write_output(output, "../data/output/sorted-20160415.tsv")

