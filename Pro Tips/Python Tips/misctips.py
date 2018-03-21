#https://stackoverflow.com/questions/25657705/make-os-listdir-list-complete-paths
# Sort data files by last update
import os
DATA_DIR = 'data'
files = sorted(os.listdir(DATA_DIR), key=lambda fn:os.path.getctime(os.path.join(DATA_DIR, fn)))
