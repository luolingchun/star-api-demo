import os

DATA_DIR = "/data/data"
FILE_PATH: str = os.path.join(DATA_DIR, "files")
for d in [FILE_PATH]:
    if not os.path.exists(d):
        os.makedirs(d)
