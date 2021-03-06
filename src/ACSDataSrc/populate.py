# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-
from Pydb import Mysql
import os
import csv
import re


class Populate():
    """Builds the census_2010_schema with various tables.

    loads: census_2010 zips and tract ids.
    loads: US geo details for all states, counties, cities with zip, lat/long.
    """

    def __init__(self):
        """Constructor for Populate"""
        self.acsdb = Mysql("../Pydb/mysql_config.yml")

    def destroy(self):
        self.acsdb.exit()

    def load_tracts(self):
        tracts = {}  # {track_id : track_name}
        with open("data/TRACT_ZIP_122015.csv") as fh:
            r_count = 0
            reader = csv.reader(fh)
            for r in reader:
                r_count += 1
                if r_count < 2:
                    continue
                tracts[r[0]] = self.get_tract_name(r[0])
        with self.acsdb.con.cursor() as cursor:
            test_sql = "SELECT * FROM census_tract_2010"
            cursor.execute(test_sql, ())
            ret = cursor.fetchone()
            if ret is not None:
                print("census_tract_2010 table already exists. Skipping...")
                return
            for t in tracts:
                update_sql = "INSERT INTO `census_tract_2010` (`track_id`, `track_name`) VALUES (%s, %s)"
                try:
                    cursor.execute(update_sql, (t, tracts[t]))
                except:
                    pass
                self.acsdb.con.commit()

    @staticmethod
    def get_tract_name(tract_id):
        """Pulls out the Census Tract Name from up to the last 6 digits in the track_id.
        This is not finished since it is taking 020100 and yielding 0201.00 and it should
        drop the initial 0 and for suffixes with no information it should drop 00.

        :param tract_id: this is the full tract id from the input file
        """
        base = re.search(r'\d+(\d{4})(\d\d)', tract_id)
        name = ".".join((base.group(1), base.group(2)))
        return name

    def load_zip_tract_crosswalk(self):
        data = []
        with open("data/TRACT_ZIP_122015.csv") as fh:
            reader = csv.reader(fh)
            index = 0
            for r in reader:
                index += 1
                if index < 2:  # skip header
                    continue
                data.append([r[0], r[1], r[2], r[3], r[4], r[5]])  # TRACT,ZIP,RES_RATIO,BUS_RATIO,OTH_RATIO,TOT_RATIO
        with self.acsdb.con.cursor() as cursor:
            test_sql = "SELECT * FROM zip_tract_cw"
            cursor.execute(test_sql, ())
            ret = cursor.fetchone()
            if ret is not None:
                print("zip_tract_cw table already exists. Skipping...")
                return
            for r in data:
                zip_id_sql = "SELECT `pk_id` FROM `zip` WHERE `zipcode`=%s"
                cursor.execute(zip_id_sql, (r[1]))
                zip_pk_id = cursor.fetchone()
                if zip_pk_id is None:
                    print(r[1])
                track_id_sql = "SELECT `pk_id` FROM `census_tract_2010` WHERE `track_id`=%s"
                cursor.execute(track_id_sql, (r[0]))
                track_pk_id = cursor.fetchone()
                if track_pk_id is None:
                    print(r[0])
                    continue
                insert_sql = "INSERT INTO `zip_tract_cw` " \
                             "(`track_pk_id`, " \
                             "`zip_pk_id`, " \
                             "`res_ratio`, " \
                             "`bus_ratio`, " \
                             "`oth_ratio`, " \
                             "`tot_ratio`) " \
                             "VALUES (%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(insert_sql, (track_pk_id['pk_id'], zip_pk_id['pk_id'], r[2], r[3], r[4], r[5]))
                    self.acsdb.con.commit()
                except Exception as e:
                    print("tract %s attempted to map into zip %s and not found - %s" % (r[0], r[1], e))

    def load_geo_details(self):
        geo = {}
        with open("data/US/US.txt") as fh:
            reader = csv.reader(fh, delimiter='\t')
            for r in reader:
                geo[r[1]] = [{'city': r[2]}, {'county': r[5]}, {'state': r[3]}, {'lat': r[9]}, {'lon': r[10]}]
        with self.acsdb.con.cursor() as cursor:
            test_sql = "SELECT * FROM zip"
            cursor.execute(test_sql, ())
            ret = cursor.fetchone()
            if ret is not None:
                print("Zip table already exists. Skipping...")
                return
            for g in geo:
                update_sql = "INSERT INTO `zip` (`city`, `county`, `state`, `lat`, `lon`, `zipcode`) " \
                             "VALUES (%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(update_sql, (geo[g][0]['city'],
                                                geo[g][1]['county'],
                                                geo[g][2]['state'],
                                                geo[g][3]['lat'],
                                                geo[g][4]['lon'],
                                                g))
                except:
                    pass
                self.acsdb.con.commit()

    def load_S2503(self):
        data = {}
        with open("data/ACS_14_5YR_S2503.csv") as fh:
            reader = csv.reader(fh)
            r_count = 0
            for r in reader:
                r_count += 1
                if r_count < 3:
                    continue
                # name = re.search(r'[\w .]+', r[2]).group(0)
                r = [e.replace('-', '0') for e in r]
                r = [e.replace('(X)', '0') for e in r]
                r = [e.replace('250,000+', '250000') for e in r]
                r = [e.replace('***', '0') for e in r]
                r = [e.replace('**', '0') for e in r]
                data[r[1]] = [{'HC01_VC01': float(r[3])},
                              {'HC02_VC01': float(r[5])},
                              {'HC03_VC01': float(r[7])},
                              {'HC01_VC03': float(r[9])},
                              {'HC02_VC03': float(r[11])},
                              {'HC03_VC03': float(r[13])},
                              {'HC01_VC04': float(r[15])},
                              {'HC02_VC04': float(r[17])},
                              {'HC03_VC04': float(r[19])},
                              {'HC01_VC05': float(r[21])},
                              {'HC02_VC05': float(r[23])},
                              {'HC03_VC05': float(r[25])},
                              {'HC01_VC06': float(r[27])},
                              {'HC02_VC06': float(r[29])},
                              {'HC03_VC06': float(r[31])},
                              {'HC01_VC07': float(r[33])},
                              {'HC02_VC07': float(r[35])},
                              {'HC03_VC07': float(r[37])},
                              {'HC01_VC08': float(r[39])},
                              {'HC02_VC08': float(r[41])},
                              {'HC03_VC08': float(r[43])},
                              {'HC01_VC09': float(r[45])},
                              {'HC02_VC09': float(r[47])},
                              {'HC03_VC09': float(r[49])},
                              {'HC01_VC10': float(r[51])},
                              {'HC02_VC10': float(r[53])},
                              {'HC03_VC10': float(r[55])},
                              {'HC01_VC11': float(r[57])},
                              {'HC02_VC11': float(r[59])},
                              {'HC03_VC11': float(r[61])},
                              {'HC01_VC12': float(r[63])},
                              {'HC02_VC12': float(r[65])},
                              {'HC03_VC12': float(r[67])},
                              {'HC01_VC13': float(r[69])},
                              {'HC02_VC13': float(r[71])},
                              {'HC03_VC13': float(r[73])},
                              {'HC01_VC14': float(r[75])},
                              {'HC02_VC14': float(r[77])},
                              {'HC03_VC14': float(r[79])}]
        with self.acsdb.con.cursor() as cursor:
            test_sql = "SELECT * FROM S2503_ACS"
            cursor.execute(test_sql, ())
            ret = cursor.fetchone()
            if ret is not None:
                print("S2503_ACS table already exists. Skipping...")
                return
            for r in data:
                get_track_id_sql = "SELECT `pk_id` FROM `census_tract_2010` AS c WHERE `track_id`=%s"
                cursor.execute(get_track_id_sql, (r))
                track_pk_id = cursor.fetchone()
                if track_pk_id is None:
                    continue
                update_sql = "INSERT INTO `S2503_ACS` " \
                             "(`HC01_VC01`, `HC02_VC01`, `HC03_VC01`, " \
                             "`HC01_VC03`, `HC02_VC03`, `HC03_VC03`, " \
                             "`HC01_VC04`, `HC02_VC04`, `HC03_VC04`, " \
                             "`HC01_VC05`, `HC02_VC05`, `HC03_VC05`, " \
                             "`HC01_VC06`, `HC02_VC06`, `HC03_VC06`, " \
                             "`HC01_VC07`, `HC02_VC07`, `HC03_VC07`, " \
                             "`HC01_VC08`, `HC02_VC08`, `HC03_VC08`, " \
                             "`HC01_VC09`, `HC02_VC09`, `HC03_VC09`, " \
                             "`HC01_VC10`, `HC02_VC10`, `HC03_VC10`, " \
                             "`HC01_VC11`, `HC02_VC11`, `HC03_VC11`, " \
                             "`HC01_VC12`, `HC02_VC12`, `HC03_VC12`, " \
                             "`HC01_VC13`, `HC02_VC13`, `HC03_VC13`, " \
                             "`HC01_VC14`, `HC02_VC14`, `HC03_VC14`, " \
                             "`track_pk_id`) " \
                             "VALUES " \
                             "(%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s)"
                try:
                    cursor.execute(update_sql, (data[r][0]['HC01_VC01'], data[r][1]['HC02_VC01'], data[r][2]['HC03_VC01'],
                                                data[r][3]['HC01_VC03'], data[r][4]['HC02_VC03'], data[r][5]['HC03_VC03'],
                                                data[r][6]['HC01_VC04'], data[r][7]['HC02_VC04'], data[r][8]['HC03_VC04'],
                                                data[r][9]['HC01_VC05'], data[r][10]['HC02_VC05'], data[r][11]['HC03_VC05'],
                                                data[r][12]['HC01_VC06'], data[r][13]['HC02_VC06'], data[r][14]['HC03_VC06'],
                                                data[r][15]['HC01_VC07'], data[r][16]['HC02_VC07'], data[r][17]['HC03_VC07'],
                                                data[r][18]['HC01_VC08'], data[r][19]['HC02_VC08'], data[r][20]['HC03_VC08'],
                                                data[r][21]['HC01_VC09'], data[r][22]['HC02_VC09'], data[r][23]['HC03_VC09'],
                                                data[r][24]['HC01_VC10'], data[r][25]['HC02_VC10'], data[r][26]['HC03_VC10'],
                                                data[r][27]['HC01_VC11'], data[r][28]['HC02_VC11'], data[r][29]['HC03_VC11'],
                                                data[r][30]['HC01_VC12'], data[r][31]['HC02_VC12'], data[r][32]['HC03_VC12'],
                                                data[r][33]['HC01_VC13'], data[r][34]['HC02_VC13'], data[r][35]['HC03_VC13'],
                                                data[r][36]['HC01_VC14'], data[r][37]['HC02_VC14'], data[r][38]['HC03_VC14'],
                                                track_pk_id['pk_id']))
                except Exception as e:
                    print(e)
                self.acsdb.con.commit()

    def load_S2503_moe(self):  # TODO: Should refactor this to fold MOE into data load...Needs new ddl as well
        """
        Same general method as load_S2503 but this loads the MOE for each variable in the dataset.
        :return:
        """
        data = {}
        with open("data/ACS_14_5YR_S2503.csv") as fh:
            reader = csv.reader(fh)
            r_count = 0
            for r in reader:
                r_count += 1
                if r_count < 3:
                    continue
                # name = re.search(r'[\w .]+', r[2]).group(0)
                r = [e.replace('-', '0') for e in r]
                r = [e.replace('(X)', '0') for e in r]
                r = [e.replace('250,000+', '250000') for e in r]
                r = [e.replace('***', '0') for e in r]
                r = [e.replace('**', '0') for e in r]
                data[r[1]] = [{'HC01_VC01_MOE': float(r[4])},
                              {'HC02_VC01_MOE': float(r[6])},
                              {'HC03_VC01_MOE': float(r[8])},
                              {'HC01_VC03_MOE': float(r[10])},
                              {'HC02_VC03_MOE': float(r[12])},
                              {'HC03_VC03_MOE': float(r[14])},
                              {'HC01_VC04_MOE': float(r[16])},
                              {'HC02_VC04_MOE': float(r[18])},
                              {'HC03_VC04_MOE': float(r[20])},
                              {'HC01_VC05_MOE': float(r[22])},
                              {'HC02_VC05_MOE': float(r[24])},
                              {'HC03_VC05_MOE': float(r[26])},
                              {'HC01_VC06_MOE': float(r[28])},
                              {'HC02_VC06_MOE': float(r[30])},
                              {'HC03_VC06_MOE': float(r[32])},
                              {'HC01_VC07_MOE': float(r[34])},
                              {'HC02_VC07_MOE': float(r[36])},
                              {'HC03_VC07_MOE': float(r[38])},
                              {'HC01_VC08_MOE': float(r[40])},
                              {'HC02_VC08_MOE': float(r[42])},
                              {'HC03_VC08_MOE': float(r[44])},
                              {'HC01_VC09_MOE': float(r[46])},
                              {'HC02_VC09_MOE': float(r[48])},
                              {'HC03_VC09_MOE': float(r[50])},
                              {'HC01_VC10_MOE': float(r[52])},
                              {'HC02_VC10_MOE': float(r[54])},
                              {'HC03_VC10_MOE': float(r[56])},
                              {'HC01_VC11_MOE': float(r[58])},
                              {'HC02_VC11_MOE': float(r[60])},
                              {'HC03_VC11_MOE': float(r[62])},
                              {'HC01_VC12_MOE': float(r[64])},
                              {'HC02_VC12_MOE': float(r[66])},
                              {'HC03_VC12_MOE': float(r[68])},
                              {'HC01_VC13_MOE': float(r[70])},
                              {'HC02_VC13_MOE': float(r[72])},
                              {'HC03_VC13_MOE': float(r[74])},
                              {'HC01_VC14_MOE': float(r[76])},
                              {'HC02_VC14_MOE': float(r[78])},
                              {'HC03_VC14_MOE': float(r[80])}]
        with self.acsdb.con.cursor() as cursor:
            test_sql = "SELECT HC01_VC01_MOE FROM S2501_ACS"
            cursor.execute(test_sql, ())
            ret = cursor.fetchone()
            if ret is not None:
                print("S2501_ACS table already provisioned with MOEs. Skipping...")
                return
            for r in data:
                get_track_id_sql = "SELECT `pk_id` FROM `census_tract_2010` AS c WHERE `track_id`=%s"
                cursor.execute(get_track_id_sql, (r))
                track_pk_id = cursor.fetchone()
                if track_pk_id is None:
                    continue
                get_pk_id_sql = "SELECT pk_id FROM S2503_ACS WHERE track_pk_id=%s"
                cursor.execute(get_pk_id_sql, (track_pk_id['pk_id']))
                ret = cursor.fetchone()
                update_sql = "UPDATE `S2503_ACS` SET " \
                             "`HC01_VC01_MOE`=%s, `HC02_VC01_MOE`=%s, `HC03_VC01_MOE`=%s, " \
                             "`HC01_VC03_MOE`=%s, `HC02_VC03_MOE`=%s, `HC03_VC03_MOE`=%s, " \
                             "`HC01_VC04_MOE`=%s, `HC02_VC04_MOE`=%s, `HC03_VC04_MOE`=%s, " \
                             "`HC01_VC05_MOE`=%s, `HC02_VC05_MOE`=%s, `HC03_VC05_MOE`=%s, " \
                             "`HC01_VC06_MOE`=%s, `HC02_VC06_MOE`=%s, `HC03_VC06_MOE`=%s, " \
                             "`HC01_VC07_MOE`=%s, `HC02_VC07_MOE`=%s, `HC03_VC07_MOE`=%s, " \
                             "`HC01_VC08_MOE`=%s, `HC02_VC08_MOE`=%s, `HC03_VC08_MOE`=%s, " \
                             "`HC01_VC09_MOE`=%s, `HC02_VC09_MOE`=%s, `HC03_VC09_MOE`=%s, " \
                             "`HC01_VC10_MOE`=%s, `HC02_VC10_MOE`=%s, `HC03_VC10_MOE`=%s, " \
                             "`HC01_VC11_MOE`=%s, `HC02_VC11_MOE`=%s, `HC03_VC11_MOE`=%s, " \
                             "`HC01_VC12_MOE`=%s, `HC02_VC12_MOE`=%s, `HC03_VC12_MOE`=%s, " \
                             "`HC01_VC13_MOE`=%s, `HC02_VC13_MOE`=%s, `HC03_VC13_MOE`=%s, " \
                             "`HC01_VC14_MOE`=%s, `HC02_VC14_MOE`=%s, `HC03_VC14_MOE`=%s " \
                             "WHERE " \
                             "pk_id=%s"
                try:
                    cursor.execute(update_sql, (data[r][0]['HC01_VC01_MOE'], data[r][1]['HC02_VC01_MOE'], data[r][2]['HC03_VC01_MOE'],
                                                data[r][3]['HC01_VC03_MOE'], data[r][4]['HC02_VC03_MOE'], data[r][5]['HC03_VC03_MOE'],
                                                data[r][6]['HC01_VC04_MOE'], data[r][7]['HC02_VC04_MOE'], data[r][8]['HC03_VC04_MOE'],
                                                data[r][9]['HC01_VC05_MOE'], data[r][10]['HC02_VC05_MOE'], data[r][11]['HC03_VC05_MOE'],
                                                data[r][12]['HC01_VC06_MOE'], data[r][13]['HC02_VC06_MOE'], data[r][14]['HC03_VC06_MOE'],
                                                data[r][15]['HC01_VC07_MOE'], data[r][16]['HC02_VC07_MOE'], data[r][17]['HC03_VC07_MOE'],
                                                data[r][18]['HC01_VC08_MOE'], data[r][19]['HC02_VC08_MOE'], data[r][20]['HC03_VC08_MOE'],
                                                data[r][21]['HC01_VC09_MOE'], data[r][22]['HC02_VC09_MOE'], data[r][23]['HC03_VC09_MOE'],
                                                data[r][24]['HC01_VC10_MOE'], data[r][25]['HC02_VC10_MOE'], data[r][26]['HC03_VC10_MOE'],
                                                data[r][27]['HC01_VC11_MOE'], data[r][28]['HC02_VC11_MOE'], data[r][29]['HC03_VC11_MOE'],
                                                data[r][30]['HC01_VC12_MOE'], data[r][31]['HC02_VC12_MOE'], data[r][32]['HC03_VC12_MOE'],
                                                data[r][33]['HC01_VC13_MOE'], data[r][34]['HC02_VC13_MOE'], data[r][35]['HC03_VC13_MOE'],
                                                data[r][36]['HC01_VC14_MOE'], data[r][37]['HC02_VC14_MOE'], data[r][38]['HC03_VC14_MOE'],
                                                ret['pk_id']))
                except Exception as e:
                    print(e)
                self.acsdb.con.commit()

    def load_S2501(self):
        data = {}
        with open("data/ACS_14_5YR_S2501.csv") as fh:
            reader = csv.reader(fh)
            r_count = 0
            for r in reader:
                r_count += 1
                if r_count < 3:  # csv file first two rows are not data
                    continue
                # name = re.search(r'[\w .]+', r[2]).group(0)
                r = [e.replace('-', '0') for e in r]
                r = [e.replace('(X)', '0') for e in r]
                r = [e.replace('250,000+', '250000') for e in r]
                r = [e.replace('***', '0') for e in r]
                r = [e.replace('**', '0') for e in r]
                data[r[1]] = [{'HC01_VC01': float(r[3])},
                              {'HC01_VC01_MOE': float(r[4])},
                              {'HC02_VC01': float(r[5])},
                              {'HC02_VC01_MOE': float(r[6])},
                              {'HC03_VC01': float(r[7])},
                              {'HC03_VC01_MOE': float(r[8])},
                              {'HC01_VC03': float(r[9])},
                              {'HC01_VC03_MOE': float(r[10])},
                              {'HC02_VC03': float(r[11])},
                              {'HC02_VC03_MOE': float(r[12])},
                              {'HC03_VC03': float(r[13])},
                              {'HC03_VC03_MOE': float(r[14])},
                              {'HC01_VC04': float(r[15])},
                              {'HC01_VC04_MOE': float(r[16])},
                              {'HC02_VC04': float(r[17])},
                              {'HC02_VC04_MOE': float(r[18])},
                              {'HC03_VC04': float(r[19])},
                              {'HC03_VC04_MOE': float(r[20])},
                              {'HC01_VC05': float(r[21])},
                              {'HC01_VC05_MOE': float(r[22])},
                              {'HC02_VC05': float(r[23])},
                              {'HC02_VC05_MOE': float(r[24])},
                              {'HC03_VC05': float(r[25])},
                              {'HC03_VC05_MOE': float(r[26])},
                              {'HC01_VC06': float(r[27])},
                              {'HC01_VC06_MOE': float(r[28])},
                              {'HC02_VC06': float(r[29])},
                              {'HC02_VC06_MOE': float(r[30])},
                              {'HC03_VC06': float(r[31])},
                              {'HC03_VC06_MOE': float(r[32])},
                              {'HC01_VC14': float(r[51])},
                              {'HC01_VC14_MOE': float(r[52])},
                              {'HC02_VC14': float(r[53])},
                              {'HC02_VC14_MOE': float(r[54])},
                              {'HC03_VC14': float(r[55])},
                              {'HC03_VC14_MOE': float(r[56])},
                              {'HC01_VC15': float(r[57])},
                              {'HC01_VC15_MOE': float(r[58])},
                              {'HC02_VC15': float(r[59])},
                              {'HC02_VC15_MOE': float(r[60])},
                              {'HC03_VC15': float(r[61])},
                              {'HC03_VC15_MOE': float(r[62])},
                              {'HC01_VC19': float(r[81])},
                              {'HC01_VC19_MOE': float(r[82])},
                              {'HC02_VC19': float(r[83])},
                              {'HC02_VC19_MOE': float(r[84])},
                              {'HC03_VC19': float(r[85])},
                              {'HC03_VC19_MOE': float(r[86])},
                              {'HC01_VC39': float(r[183])},
                              {'HC01_VC39_MOE': float(r[184])},
                              {'HC02_VC39': float(r[185])},
                              {'HC02_VC39_MOE': float(r[186])},
                              {'HC03_VC39': float(r[187])},
                              {'HC03_VC39_MOE': float(r[188])}]
        with self.acsdb.con.cursor() as cursor:
            test_sql = "SELECT * FROM S2501_ACS"
            cursor.execute(test_sql, ())
            ret = cursor.fetchone()
            if ret is not None:
                print("S2501_ACS table already exists. Skipping...")
                return
            for r in data:
                get_track_id_sql = "SELECT `pk_id` FROM `census_tract_2010` AS c WHERE `track_id`=%s"
                cursor.execute(get_track_id_sql, (r))
                track_pk_id = cursor.fetchone()
                if track_pk_id is None:
                    continue
                update_sql = "INSERT INTO `S2501_ACS` " \
                             "(`HC01_VC01`, `HC01_VC01_MOE`, `HC02_VC01`, `HC02_VC01_MOE`, `HC03_VC01`, `HC03_VC01_MOE`, " \
                             "`HC01_VC03`, `HC01_VC03_MOE`, `HC02_VC03`, `HC02_VC03_MOE`, `HC03_VC03`, `HC03_VC03_MOE`, " \
                             "`HC01_VC04`, `HC01_VC04_MOE`, `HC02_VC04`, `HC02_VC04_MOE`, `HC03_VC04`, `HC03_VC04_MOE`, " \
                             "`HC01_VC05`, `HC01_VC05_MOE`, `HC02_VC05`, `HC02_VC05_MOE`, `HC03_VC05`, `HC03_VC05_MOE`, " \
                             "`HC01_VC06`, `HC01_VC06_MOE`, `HC02_VC06`, `HC02_VC06_MOE`, `HC03_VC06`, `HC03_VC06_MOE`, " \
                             "`HC01_VC14`, `HC01_VC14_MOE`, `HC02_VC14`, `HC02_VC14_MOE`, `HC03_VC14`, `HC03_VC14_MOE`, " \
                             "`HC01_VC15`, `HC01_VC15_MOE`, `HC02_VC15`, `HC02_VC15_MOE`, `HC03_VC15`, `HC03_VC15_MOE`, " \
                             "`HC01_VC19`, `HC01_VC19_MOE`, `HC02_VC19`, `HC02_VC19_MOE`, `HC03_VC19`, `HC03_VC19_MOE`, " \
                             "`HC01_VC39`, `HC01_VC39_MOE`, `HC02_VC39`, `HC02_VC39_MOE`, `HC03_VC39`, `HC03_VC39_MOE`, " \
                             "`track_pk_id`) " \
                             "VALUES " \
                             "(%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s, %s, %s, %s, %s, %s, " \
                             "%s)"
                try:
                    cursor.execute(update_sql, (data[r][0]['HC01_VC01'], data[r][1]['HC01_VC01_MOE'], data[r][2]['HC02_VC01'], data[r][3]['HC02_VC01_MOE'], data[r][4]['HC03_VC01'], data[r][5]['HC03_VC01_MOE'],
                                                data[r][6]['HC01_VC03'], data[r][7]['HC01_VC03_MOE'], data[r][8]['HC02_VC03'], data[r][9]['HC02_VC03_MOE'], data[r][10]['HC03_VC03'], data[r][11]['HC03_VC03_MOE'],
                                                data[r][12]['HC01_VC04'], data[r][13]['HC01_VC04_MOE'], data[r][14]['HC02_VC04'], data[r][15]['HC02_VC04_MOE'], data[r][16]['HC03_VC04'], data[r][17]['HC03_VC04_MOE'],
                                                data[r][18]['HC01_VC05'], data[r][19]['HC01_VC05_MOE'], data[r][20]['HC02_VC05'], data[r][21]['HC02_VC05_MOE'], data[r][22]['HC03_VC05'], data[r][23]['HC03_VC05_MOE'],
                                                data[r][24]['HC01_VC06'], data[r][25]['HC01_VC06_MOE'], data[r][26]['HC02_VC06'], data[r][27]['HC02_VC06_MOE'], data[r][28]['HC03_VC06'], data[r][29]['HC03_VC06_MOE'],
                                                data[r][30]['HC01_VC14'], data[r][31]['HC01_VC14_MOE'], data[r][32]['HC02_VC14'], data[r][33]['HC02_VC14_MOE'], data[r][34]['HC03_VC14'], data[r][35]['HC03_VC14_MOE'],
                                                data[r][36]['HC01_VC15'], data[r][37]['HC01_VC15_MOE'], data[r][38]['HC02_VC15'], data[r][39]['HC02_VC15_MOE'], data[r][40]['HC03_VC15'], data[r][41]['HC03_VC15_MOE'],
                                                data[r][42]['HC01_VC19'], data[r][43]['HC01_VC19_MOE'], data[r][44]['HC02_VC19'], data[r][45]['HC02_VC19_MOE'], data[r][46]['HC03_VC19'], data[r][47]['HC03_VC19_MOE'],
                                                data[r][48]['HC01_VC39'], data[r][49]['HC01_VC39_MOE'], data[r][50]['HC02_VC39'], data[r][51]['HC02_VC39_MOE'], data[r][52]['HC03_VC39'], data[r][53]['HC03_VC39_MOE'],
                                                track_pk_id['pk_id']))
                except Exception as e:
                    print(e)
                self.acsdb.con.commit()


if __name__ == '__main__':
    pop = Populate()
    pop.load_tracts()
    pop.load_geo_details()
    pop.load_zip_tract_crosswalk()
    pop.load_S2503()
    pop.load_S2503_moe()
    pop.load_S2501()
    pop.destroy()


