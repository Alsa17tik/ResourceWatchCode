import logging
import sys
import eeUtil
import os
from datetime import datetime

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
eeUtil.initJson()

GS_FOLDER = 'broad_age_groups'
EE_COLLECTION = 'soc_075_broad_age_groups/{}'
def ic(asset):
    return EE_COLLECTION.format(os.split.ext(asset)[0])

# Make sure your data is in the rasters folder
DATA_DIR = 'rasters'
os.chdir(DATA_DIR)
tifs = [os.listdir('.')]
logging.info('TIFS: {}'.format(tifs))

# Update this manually, or with a function of the tif name
DATE_FORMAT = '%Y'
dates = ['2010', '2010', '2010', '2010', '2010', '2010']
datestamps = [datetime.strptime(date, DATE_FORMAT)
              for date in dates]

asset_names = [ic(t) for t in tifs]
eeUtil.uploadAssets(tifs, asset_names, GS_FOLDER, datestamps)
