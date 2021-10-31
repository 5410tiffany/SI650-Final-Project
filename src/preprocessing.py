import os, json
from tqdm import tqdm, trange
from pathlib import Path

cwd = Path(os.getcwd())

path_dataset = os.path.join( cwd.parent.absolute(),'dataset' )
path_data_txt  = os.path.join(  path_dataset,'data_txt'  )
path_data_json = os.path.join(  path_dataset,'data_json'  )

for filename in os.listdir(path_data_txt):
    path_in  = os.path.join( path_data_txt, filename  )
    path_out = os.path.join( path_data_json, filename[:-3]+'json') 
    #print(path_in)
    #print(path_out)
    with open(path_in) as f:
        lines = f.readlines()
        #print(lines[1].rstrip(), lines[1].rstrip()=="")
        mode = None
        profile = {
            "Education":[],
            "Experience":[]
        }
        num_lines = len(lines)
        idx_line = 0
        mode = None
        
        while idx_line < num_lines:
            line = lines[idx_line].rstrip()
            if line == "-----Education-----":
                mode = "Education"
                content = []
            
            elif line == "-----Experience-----":
                mode = 'Experience'
                content = []

            elif line == "":
                if mode == "Education":
                    ### content -> object
                    assert len(content) == 4
                    obj = {
                        "school": content[0],
                        "degree": content[1],
                        "major": content[2],
                        "period": content[3]
                    }

                    ### put the object into profile.Education
                    profile['Education'].append(obj)

                    ### reset content
                    content = []

                elif mode == "Experience":
                    ### content -> object
                    assert len(content) >= 4
                    obj = {
                        "title": content[0],
                        "company": content[1],
                        "period": content[2],
                        "description": ""
                    }
                    obj['description'] =  "\n".join( content[3:] )

                    ### put the object into profile.Experience
                    profile['Experience'].append(obj)

                    ### reset content
                    content = []

            else:
                #print(line)
                content.append(line)
            idx_line += 1

        with open(path_out, "w") as outfile:
            json.dump(profile, outfile,indent=4)

                

