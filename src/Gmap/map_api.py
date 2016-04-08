# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-
"""
Class that will make a search for nearby places of a particular type given a lat, long
"""

from loggerUtils import init_logging
import logging
import yaml
import json
import time
from gmaps import Geocoding, client
from urllib.request import Request
from urllib.request import urlopen


class Gmap():
    """
    """

    def __init__(self,):
        """Constructor for Gmap"""
        init_logging()
        self.logger = logging.getLogger()
        with open("Gmap/google_config.yml", 'r') as f:  #  TODO: needs to look in same dir
            settings = yaml.load(f)
        self.api_key = settings['GOOGLE_API_KEY']
        self.search_type = settings['GOOGLE_SEARCH_METHOD']

    def fetch_details(self, place_id):
        """
        Takes a valid google place id and fetches a detail entry for place.
        :param place_id:
        :return:
        """
        resultsList = []
        r = self._get_details(place_id)
        if r['status'] == 'OVER_QUERY_LIMIT':
            self.logger.warn("Google quota exceeded. Cool down!")
            return []
        resultsList = r['result']
        self.logger.info("Google details fetched for %s" % resultsList['name'])
        return resultsList

    def fetch_results(self, coords, rad=1000):
        """
        Takes a coordinate tuple and a radius and fetches a result set.
        Predetermined url at this point.
        :param coords: a tuple of lat and long for this search
        :param rad: radius of search
        :return: list of json results
        """
        resultsList = []
        r = self._search_google(coords[0], coords[1], rad)
        if r['status'] == 'OVER_QUERY_LIMIT':
            self.logger.warn("Google quota exceeded. Cool down!")
            return []
        for place in r['results']:
            resultsList.append(place)
        if 'next_page_token' in r:
            time.sleep(2)
            while True:
                npt = r['next_page_token']
                r = self._search_google(coords[0], coords[1], rad, npt)
                for place in r['results']:
                    resultsList.append(place)
                try:
                    r['next_page_token']
                except:
                    break
        self.logger.info("Google maps searched and results returned for %s, %s." % (coords[0], coords[1]))
        return resultsList, self.search_type

    def _get_details(self, place_id):
        """
        Builds and executes a REST query for details about a google place with place_id
        :param place_id:  valid google places place_id
        :return:
        """
        url = self._build_details_url(place_id)
        req = Request(url)
        r = json.loads(urlopen(req).read().decode('utf-8'))
        return r

    def _search_google(self, lat, long, r, npt=None):
        """
        Builds and executes a REST API for searching places, with pagination control
        :param lat:
        :param long:
        :param r:
        :param npt:
        :return:
        """
        url = self._build_search_url(lat, long, radius=r, npt=npt)
        req = Request(url)
        r = json.loads(urlopen(req).read().decode('utf-8'))
        return r

    def _build_details_url(self, place_id):
        """
        Builds up REST API query for Google Places API details retrieve
        :param place_id:
        :return:
        """
        url = 'https://maps.googleapis.com/maps/api/place/details/json?'
        url += 'placeid='
        url += str(place_id)
        url += '&key='
        url += self.api_key
        return url

    def _build_search_url(self, lat, long, radius=5000, npt=None):
        """
        Builds up REST API query for Google Maps API nearby places search
        :param lat:
        :param long:
        :param radius:
        :param npt: the next page token returned from google, if there is one.
        :return:
        """
        url = 'https://maps.googleapis.com/maps/api/place/'
        if self.search_type == 'nearby':
            url += 'nearbysearch/'
        elif self.search_type == 'radar':
            url += 'radarsearch/'
        else:
            print ("No search type specified in google config!")
            exit()
        url += 'json?location='
        url += str(lat)
        url += ','
        url += str(long)
        url += '&radius='
        url += str(radius)
        url += '&types=car_dealer'
        #url += '&keyword=laundromat'  # keyword: "(cinema) OR (theater)" unclear if it works
        url += '&key='
        url += self.api_key
        if npt is not None:
            url += '&pagetoken='
            url += str(npt)
        return url




if __name__ == '__main__':
    extract = Gmap()
    r = extract.fetch_results()