#!/usr/bin/env python

import csv

from dateutil.parser import *

from etc.gdocs import GoogleDoc

def write_aggregates_file():
    fieldnames = [
        'name',
        'state_fips',
        'county_fips',
        'combined_fips',
        'total_visits',
        'total_fundraising_visits',
        'total_message_visits',
        'visits_2009',
        'visits_2010',
        'visits_2011',
        'visits_2012',
        'visits_2013',
        'visits_2014',
        'fundraising_2009',
        'fundraising_2010',
        'fundraising_2011',
        'fundraising_2012',
        'fundraising_2013',
        'fundraising_2014',
        'message_2009',
        'message_2010',
        'message_2011',
        'message_2012',
        'message_2013',
        'message_2014'
    ]

    with open('data/county_aggregates.csv', 'wb') as writefile:
        csvwriter = csv.DictWriter(writefile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for county in County.objects.all():
            # from visit.models import Visit
            # """
            # total_visits,
            # total_fundraising_visits,
            # total_message_visits,
            # visits_2009,
            # visits_2010,
            # visits_2011,
            # visits_2012,
            # visits_2013,
            # visits_2014,
            # fundraising_2009,
            # fundraising_2010,
            # fundraising_2011,
            # fundraising_2012,
            # fundraising_2013,
            # fundraising_2014,
            # message_2009,
            # message_2010,
            # message_2011,
            # message_2012,
            # message_2013,
            # message_2014
            # """
            # payload = {}
            # payload['name'] = self.name
            # payload['state_fips'] = self.statefp
            # payload['county_fips'] = self.countyfp
            # payload['combined_fips'] = '%s%s' % (self.statefp, self.countyfp)

            # for key, value in payload.items():
            #     if value:
            #         payload[key] = value.encode('utf-8')
            #     else:
            #         payload[key] = None

            # payload['total_visits'] = 0
            # payload['total_fundraising_visits'] = 0
            # payload['total_message_visits'] = 0
            # payload['visits_2009'] = 0
            # payload['visits_2010'] = 0
            # payload['visits_2011'] = 0
            # payload['visits_2012'] = 0
            # payload['visits_2013'] = 0
            # payload['visits_2014'] = 0
            # payload['fundraising_2009'] = 0
            # payload['fundraising_2010'] = 0
            # payload['fundraising_2011'] = 0
            # payload['fundraising_2012'] = 0
            # payload['fundraising_2013'] = 0
            # payload['fundraising_2014'] = 0
            # payload['message_2009'] = 0
            # payload['message_2010'] = 0
            # payload['message_2011'] = 0
            # payload['message_2012'] = 0
            # payload['message_2013'] = 0
            # payload['message_2014'] = 0

            # visits = Visit.objects.filter(point__intersects=self.geom)
            # payload['total_visits'] = visits.count()

            # for visit in visits:

            #     if visit.visit_type.lower() == "fundraiser":
            #         payload['total_fundraising_visits'] += 1
            #         payload['fundraising_%s' % visit.date.year] += 1
            #     else:
            #         payload['total_message_visits'] += 1
            #         payload['message_%s' % visit.date.year] += 1

            #     payload['visits_%s' % visit.date.year] +=1

            # return payload
            csvwriter.writerow(county.visits_aggregates())


def write_visit_file():
    fieldnames = ['date', 'location', 'city', 'state', 'county', 'state_fips', 'county_fips', 'combined_fips', 'visit_type', 'description', 'link']

    with open('data/visits.csv', 'wb') as writefile:
        csvwriter = csv.DictWriter(writefile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for visit in Visit.objects.all():
            csvwriter.writerow(visit.to_dict())

def parse_csv():
    with open('data/visits.csv', 'rb') as readfile:
        visits = list(csv.DictReader(readfile))

    from django.contrib.gis.gdal import DataSource
    ds = DataSource('www/assets/shp/elpo12p010g.shp')
    layer = ds[0]

    fieldnames = ['date', 'location', 'city', 'state', 'county', '2012_obama_vote_margin', '2012_obama_vote_pct', 'state_fips', 'county_fips', 'combined_fips', 'visit_type', 'description', 'link']

    with open('data/visits-2012annotated.csv', 'wb') as writefile:
        csvwriter = csv.DictWriter(writefile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for visit in visits:
            unknown = True
            for county in layer:
                if visit['combined_fips'].zfill(5) == county['FIPS'].as_string():
                    visit['2012_obama_vote_margin'] = float(county['PCT_OBM'].as_string()) - float(county['PCT_ROM'].as_string())
                    visit['2012_obama_vote_pct'] = float(county['PCT_OBM'].as_string())
                    csvwriter.writerow(visit)
                    unknown = False
                    break
                elif (visit['state'].lower() == county['STATE'].as_string().lower()) and (visit['county'].lower() == county['COUNTY'].as_string().lower()):
                    visit['2012_obama_vote_margin'] = float(county['PCT_OBM'].as_string()) - float(county['PCT_ROM'].as_string())
                    visit['2012_obama_vote_pct'] = float(county['PCT_OBM'].as_string())
                    csvwriter.writerow(visit)
                    unknown = False
                    break
            if unknown:
                print visit['combined_fips'].zfill(5)

def download_csv():
    doc = {
        "key": "0AgtV5am-X0b8dG9qS21LQUNMSDNJakRFNkpvbFBGbVE",
        "file_name": "visits",
        "file_format": "csv",
        "gid": "7"
    }
    g = GoogleDoc(**doc)
    g.get_auth()
    g.get_document()