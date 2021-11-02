import os, json
from tqdm import tqdm, trange
from pathlib import Path

cwd = Path(os.getcwd())
path_dataset = os.path.join( cwd.parent.absolute(),'dataset' )
path_data_txt  = os.path.join(  path_dataset,'data_txt'  )
path_data_json = os.path.join(  path_dataset,'data_json'  )


for filename in os.listdir(path_data_json):
    path_in  = os.path.join( path_data_json, filename  )
    with open(path_in) as json_file:
        data = json.load(json_file)
        print('--------------------------------------------------------------')
        for idx,edu in enumerate(data['Education']):
            print(idx,edu)
        for idx,exp in enumerate(data['Experience']):
            print(idx,exp)