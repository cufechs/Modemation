import os
import shutil
import pathlib


if __name__ == '__main__' :

    MAIN_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
    
    # create 'frames' dir if not there, and if there flush it
    try: 
        shutil.rmtree(os.path.join(MAIN_DIR, 'frames'))
    except:
        pass
    finally:
        os.mkdir('frames') 
        os.mkdir('frames/pose') 
        os.mkdir('frames/initial') 

    try: 
        shutil.rmtree(os.path.join(MAIN_DIR, 'openpose/frames'))
    except:
        pass
   