import logging
import sys
import eeUtil
import os
from datetime import datetime

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
eeUtil.initJson()

# Configure the ImageCollection you're going to add the rasters to
GS_FOLDER = 'broad_age_groups'
EE_COLLECTION = 'soc_075_broad_age_groups'
def checkCreateCollection(collection):
    '''List assests in collection else create new collection'''
    if eeUtil.exists(collection):
        return eeUtil.ls(collection)
    else:
        logging.info('{} does not exist, creating'.format(collection))
        eeUtil.createFolder(collection, True, public=True)
        return []
existing_files = checkCreateCollection(EE_COLLECTION)

# Make sure your data is in the rasters folder
DATA_DIR = 'rasters'
EXTENSIONS = ['.tif', '.nc']
os.chdir(DATA_DIR)
tifs = [f for f in os.listdir('.') if os.path.splitext(f)[1] in EXTENSIONS]
logging.info('TIFS: {}'.format(tifs))

# Update this manually, or with a function of the tif name
DATE_FORMAT = '%Y'
dates = ['2010', '2010', '2010', '2010', '2010', '2010']
datestamps = [datetime.strptime(date, DATE_FORMAT)
              for date in dates]

def ic(asset):
    return '{}/{}'.format(EE_COLLECTION, os.path.splitext(asset)[0])
asset_names = [ic(t) for t in tifs]
eeUtil.uploadAssets(tifs, asset_names, GS_FOLDER, datestamps)
