from pathlib import Path

import numpy as np
from crypto_gltf.local_tests.local_paths import PAPER_DIR
from loci_io.env import MONGO_DB_URL
from loci_io.utils import get_file
from pymongo import MongoClient
from tqdm import tqdm

client = MongoClient(MONGO_DB_URL)
db = client["main"]
github_dataset_collection = db["github_assets_dataset"]
objaversexl_colleciton = db["assets_objaverse_xl"]

fails = 0
count = objaversexl_colleciton.count_documents({})
# cursor = .find({})
cursor = objaversexl_colleciton.aggregate([{"$sample": {"size": 6000}}])

for idx, doc in tqdm(enumerate(cursor), total=6000):
    try:
        path = PAPER_DIR / "xl_assets" / doc["source_id"]
        path.mkdir(exist_ok=True)
        get_file(link=doc["asset_path"], target=path)
    except:
        fails += 1
        pass

print(fails)
