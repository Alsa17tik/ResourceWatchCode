import os
import logging
import sys
import requests
from collections import OrderedDict, defaultdict
from datetime import datetime
import cartosql

# Constants
LATEST_URL = 'http://popdata.unhcr.org/api/stats/persons_of_concern_all_countries.json?year={year}'

CARTO_TABLE = 'soc_043_refugees_and_displaced_persons'
CARTO_SCHEMA = OrderedDict([
    ('_UID', 'text'),
    ('date', 'timestamp'),
    ('country', 'text'),
    ('value_type', 'text'),
    ('num_people', 'numeric')
])
UID_FIELD = '_UID'
TIME_FIELD = 'date'
DATA_DIR = 'data'
LOG_LEVEL = logging.DEBUG
DATE_FORMAT = '%Y-%m-%d'
CLEAR_TABLE_FIRST = False

# Limit 1M rows, drop older than 20yrs
MAXROWS = 1000000
MAXAGE = datetime.today().year - 20

def genUID(date, country, value_type):
    '''Generate unique id'''
    return '{}_{}_{}'.format(country, date, value_type)

def insertIfNew(country_data, existing_ids, new_ids, new_rows,
                date_format=DATE_FORMAT):
    '''Loop over months in the data, add to new rows if new'''
    year = country_data['year']
    country = country_data['country_iso']
    for origin_or_asylum in ['country_of_origin', 'country_of_asylum']:
        for poc_type, val in country_data[origin_or_asylum].items():
            date = datetime(year=year, month=12, day=31).strftime(date_format)
            value_type = '{}_{}'.format(origin_or_asylum, poc_type)
            UID = genUID(date, country, value_type)
            if UID not in existing_ids + new_ids:
                new_ids.append(UID)
                values = [UID, date, country, value_type, val]
                new_rows.append(values)

def processNewData(existing_ids):
    '''
    Iterively fetch parse and post new data
    '''
    year = datetime.today().year
    new_count = 1
    new_ids = []

    while year > MAXAGE and new_count:
        # get and parse each page; stop when no new results or 200 pages
        # 1. Fetch new data
        logging.info("Fetching data for year {}".format(year))
        r = requests.get(LATEST_URL.format(year=year))
        if 'InvalidContent' in r.text:
            logging.warning('No data for year {}'.format(year))
            new_count = 1
            year -= 1
            continue

        data = r.json()
        logging.debug('data: {}'.format(data))

        # 3. Create Unique IDs, create new rows
        new_rows = []
        for country_data in data:
            logging.debug('Data: {}'.format(country_data))
            logging.debug('Processing data for {} in year {}'.format(country_data['name'], country_data['year']))
            insertIfNew(country_data, existing_ids, new_ids, new_rows)

        # 4. Insert new rows
        new_count = len(new_rows)
        if new_count:
            logging.info('Pushing {} new rows'.format(new_count))
            cartosql.insertRows(CARTO_TABLE, CARTO_SCHEMA.keys(),
                                CARTO_SCHEMA.values(), new_rows)
        # Decrement year
        year -= 1

    num_new = len(new_ids)
    return num_new


##############################################################
# General logic for Carto
# should be the same for most tabular datasets
##############################################################

def createTableWithIndex(table, schema, id_field, time_field=''):
    '''Get existing ids or create table'''
    cartosql.createTable(table, schema)
    cartosql.createIndex(table, id_field, unique=True)
    if time_field and time_field!= id_field:
        cartosql.createIndex(table, time_field)


def getIds(table, id_field):
    '''get ids from table'''
    r = cartosql.getFields(id_field, table, f='csv')
    return r.text.split('\r\n')[1:-1]

def deleteExcessRows(table, max_rows, time_field, max_age=''):
    '''Delete excess rows by age or count'''
    num_dropped = 0
    if isinstance(max_age, datetime):
        max_age = max_age.isoformat()

    # 1. delete by age
    if max_age:
        r = cartosql.deleteRows(table, "{} < '{}'".format(time_field, max_age))
        num_dropped = r.json()['total_rows']

    # 2. get sorted ids (old->new)
    r = cartosql.getFields('cartodb_id', table, order='{}'.format(time_field),
                           f='csv')
    ids = r.text.split('\r\n')[1:-1]

    # 3. delete excess
    if len(ids) > max_rows:
        r = cartosql.deleteRowsByIDs(table, ids[:-max_rows])
        num_dropped += r.json()['total_rows']
    if num_dropped:
        logging.info('Dropped {} old rows from {}'.format(num_dropped, table))


def main():
    logging.basicConfig(stream=sys.stderr, level=LOG_LEVEL)
    logging.info('STARTING')

    if CLEAR_TABLE_FIRST:
        logging.info('Clearing table')
        cartosql.dropTable(CARTO_TABLE)

    # 1. Check if table exists and create table
    existing_ids = []
    if cartosql.tableExists(CARTO_TABLE):
        logging.info('Fetching existing ids')
        existing_ids = getIds(CARTO_TABLE, UID_FIELD)
    else:
        logging.info('Table {} does not exist, creating'.format(CARTO_TABLE))
        createTableWithIndex(CARTO_TABLE, CARTO_SCHEMA, UID_FIELD, TIME_FIELD)

    # 2. Iterively fetch, parse and post new data
    num_new = processNewData(existing_ids)

    existing_count = num_new + len(existing_ids)
    logging.info('Total rows: {}, New: {}, Max: {}'.format(
        existing_count, num_new, MAXROWS))

    # 3. Remove old observations
    deleteExcessRows(CARTO_TABLE, MAXROWS, TIME_FIELD, datetime(year=MAXAGE, month=1, day=1))

    logging.info('SUCCESS')
