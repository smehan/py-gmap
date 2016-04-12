# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-

# standard modules
import logging
import csv
import os
import sys
import time
import random
# 3rd party modules
from Gmap import map_api as goog
# Application modules
from loggerUtils import init_logging


class Dealer(object):
    """Will build up coordinates for a state, then will fetch unique places from
    Google Places API, fetch details for each place, write output to a TSV."""
    def __init__(self, state_name='WA'):
        """Constructor for Dealer search object"""
        init_logging()
        self.logger = logging.getLogger()
        self.logger.info("Bishop Car Dealer Search object initialized and logging enabled...")

        self.gfind = goog.Gmap()
        self.state_name = state_name
        self.outfile = '../data/output/{}.tsv'.format(self.state_name)
        self.fieldnames = (
            'name',
            'web',
            'address',
            'city',
            'state',
            'zip',
            'phone'
        )

    def destroy(self):
        """
        method to cleanly destroy all objects
        :return:
        """
        self.logger.info("Bishop Car Dealer Search object destroyed "
                         "and {} job finished....".format(self.state_name))

    def get_coords(self, f):
        """
        Reads in all zips and outputs a data structure with required zips: (lat, long)
        :param f: file path to zip file.
        :return: dictionary of {zips: (lat, long)}
        """
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f), 'r') as fh:
            data = {}
            for line in fh:
                parts = line.split('\t')
                if self.state_name not in parts[4]:
                    continue
                c = (parts[9], parts[10].strip())
                if c not in data.values():
                    data[parts[1]] = c
            self.logger.info('Zip coordinates built for {state}. '
                             '{points} total points to search...'.format(state=self.state_name,
                                                                         points=len(data)))
            return data

    def _init_output(self):
        if not os.path.exists(self.outfile):
            with open(self.outfile, 'w', encoding='utf-8') as fh:
                outwriter = csv.DictWriter(fh,
                                           fieldnames=self.fieldnames,
                                           delimiter='\t')
                outwriter.writeheader()

    def process_output(self, r):
        self._init_output()
        with open(self.outfile, 'a', encoding='utf-8') as fh:
            outwriter = csv.DictWriter(fh,
                                       fieldnames=self.fieldnames,
                                       delimiter='\t')
            outwriter.writerow(r)

    def _add_places(self, result, data):
        for e in result:
            place_id = e['place_id']
            if place_id not in data:
                data[place_id] = {'name': e['name']}
                data = self._add_details(place_id, data)
                self.process_output(data[place_id])
                data[place_id] = {}
        return data

    def _add_details(self, p_id, data):
        """
        Updates a dict entry for place with place_id with google place details
        :param p_id: google place id to be pulled
        :param data: dict to write results into and return
        :return: return dict with new entry details
        """
        try:
            result = self.gfind.fetch_details(p_id)
        except:
            return data
        if data[p_id]['name'] != result['name']:
            return data
        elif len(result['address_components']) >= 6:
            data[p_id]['address'] = result['address_components'][0]['long_name'] + \
                                    " " + result['address_components'][1]['long_name']
            data[p_id]['city'] = result['address_components'][2]['long_name']
            data[p_id]['state'] = result['address_components'][3]['short_name']
            data[p_id]['zip'] = result['address_components'][5]['long_name']
            data[p_id]['phone'] = result.get('formatted_phone_number', '')
            data[p_id]['web'] = result.get('website', '')
        else:
            data[p_id]['address'] = result.get('formatted_address', '')
            data[p_id]['city'] = result.get('formatted_address', '')
            data[p_id]['state'] = result.get('formatted_address', '')
            data[p_id]['zip'] = result.get('formatted_address', '')
            data[p_id]['phone'] = result.get('formatted_phone_number', '')
            data[p_id]['web'] = result.get('website', '')
        return data

    def get_places(self, zips):
        """
        Iterates through all zip codes to search for places. Maintains
        an locally scoped data structure, places.
        :param zips: dictionary of {zips: (lat, long)}
        :return:
        """
        places = {}
        index = 0  # used for progress meter
        for k in zips:
            self.imitate_user(0.05)
            index += 1
            result = []
            coords = zips[k]
            result, search_type = self.gfind.fetch_results(coords, rad=30000)
            places = self._add_places(result, places)
            self._zip_progress(index, len(zips))

    def _zip_progress(self, part, total):
        """
        Displays a progress bar to indicate current search progress.
        :param part: the portion searched
        :param total: the total to search
        :return:
        """
        self.logger.info('{}%% complete.'.format(round((part/total)*100, 2)))

    @staticmethod
    def imitate_user(top=1.0):
        """
        This will cause system to pause for top*60 seconds. Makes a random
        pause on each call, to create random variability in browser requests.
        :param top: number of minutes to delay before next http call.
        :return:
        """
        random.seed()
        delay = random.random()*top*60  # time.sleep expects seconds
        time.sleep(delay)

if __name__ == '__main__':
    dealer = Dealer('MN')  # init a new search object with the names state to be searched
    zips_dict = dealer.get_coords('../data/input/US-zips.txt')
    dealer.get_places(zips_dict)
    dealer.destroy()
    sys.exit()


