# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-
"""
Class that will make a search for nearby places of a particular type given a lat, long
"""

# standard modules
import logging
import json
import time
import os
from urllib.request import Request
from urllib.request import urlopen
# 3rd party modules
import yaml
# application modules
from loggerUtils import init_logging


class Gmap(object):
    """
    """
    def __init__(self,):
        """Constructor for Gmap"""
        init_logging()
        self.logger = logging.getLogger()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "google_config.yml"), "r") as fh:
            settings = yaml.load(fh)
        self.api_key = settings['GOOGLE_API_KEY']
        self.search_type = settings['GOOGLE_SEARCH_METHOD']

    def fetch_details(self, place_id):
        """
        Takes a valid google place id and fetches a detail entry for place.
        :param place_id:
        :return: results as a list
        """
        r = self._get_details(place_id)
        if r is None:
            self.logger.warn('Failure to return details from google API'
                             ' for {}'.format(place_id))
            return []
        if r['status'] == 'OVER_QUERY_LIMIT':
            self.logger.warn("Google quota exceeded. Cool down!")
            return []
        results_list = r['result']
        self.logger.info("Google details fetched for %s" % results_list['name'])
        return results_list

    def fetch_results(self, coords, rad=1000, place_type=None, keywords=None):
        """
        Takes a coordinate tuple and a radius and fetches a result set.
        Predetermined url at this point.
        :param coords: a tuple of lat and long for this search
        :param rad: radius of search
        :param place_type: a valid google place type
        :param keywords: a tuple of keywords to search on
        :return: list of json results, search_type executed
        """
        r = self._search_google(coords[0], coords[1], rad, place_type, keywords)
        if r is None:
            self.logger.warn('Failure to return search from google API'
                             ' for {lat}, {long}'.format(lat=coords[0],
                                                         long=coords[1]))
            return []
        elif r['status'] == 'OVER_QUERY_LIMIT':
            self.logger.warn("Google quota exceeded. Cool down!")
            return []
        results_list = []
        [results_list.append(place) for place in r['results']]
        if 'next_page_token' in r:
            time.sleep(2)
            while True:
                npt = r['next_page_token']
                r = self._search_google(coords[0], coords[1], rad, place_type, keywords, npt)
                [results_list.append(place) for place in r['results']]
                try:
                    r['next_page_token']
                except Exception as e:
                    self.logger.error("Error fetching next page from Google: {}".format(e))
                    break
        self.logger.info("Google maps searched and results returned for %s, %s." % (coords[0], coords[1]))
        return results_list, self.search_type

    def _make_request(self, request_url):
        """
        Builds a HTTP Request object then opens and reads data from that object.
        :param request_url: URL to use for request
        :return: json payload from URL
        """
        req = Request(request_url)
        with urlopen(req) as rh:
            try:
                response = json.loads(rh.read().decode('utf-8'))
                return response
            except Exception as e:
                self.logger.error(e)
                return None

    def _get_details(self, place_id):
        """
        Builds and executes a REST query for details about a google place with place_id
        :param place_id: valid google places place_id
        :return:
        """
        url = self._build_details_url(place_id)
        return self._make_request(url)

    def _build_details_url(self, place_id):
        """
        Builds up REST API query for Google Places API details retrieve
        :param place_id:
        :return: the fully formed url
        """
        url = 'https://maps.googleapis.com/maps/api/place/details/json?'
        url += 'placeid='
        url += str(place_id)
        url += '&key='
        url += self.api_key
        return url

    def _search_google(self, lat, long, radius, place_type, keywords, npt=None):
        """
        Builds and executes a REST API call
        for searching places, including param for pagination control
        :param lat:
        :param long:
        :param radius: raidus to use for radar search
        :param keywords: a tuple of keywords to search on
        :param npt: next page token from multi-page search result
        :return:
        """
        url = self._build_search_url(lat, long, radius=radius,
                                     place_type=place_type, keywords=keywords, npt=npt)
        return self._make_request(url)

    def _build_search_url(self, lat, long, radius=5000, place_type=None, keywords=None, npt=None):
        """
        Builds up REST API query for Google Maps API nearby places search
        :param lat:
        :param long:
        :param radius:
        :type place_type: str
        :param place_type: optional flag for which google place type to search on
        :type keywords: tuple
        :param keywords: optional tuple of keywords to use for search
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
        if place_type:
            url += '&types='
            url += place_type
        if keywords:
            url += '&keyword='
            if len(keywords) == 1:
                url += keywords[0]
            else: # only one so no OR needed
                url += "OR".join(('(' + x + ')' for x in keywords))
        url += '&key='
        url += self.api_key
        if npt is not None:
            url += '&pagetoken='
            url += str(npt)
        return url


if __name__ == '__main__':
    extract = Gmap()
    r = extract.fetch_results()