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
        shutil.rmtree(os.path.join(MAIN_DIR, 'test'))
    except:
        pass
    finally:
        os.mkdir('test')

    try: 
        shutil.rmtree(os.path.join(MAIN_DIR, 'openpose/frames'))
    except:
        pass
        
    try: 
        shutil.rmtree(os.path.join(MAIN_DIR, 'model_output'))
    except:
        pass
        
    
    HUMAN3D_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '\\Human3D'
    try: 
        shutil.rmtree(os.path.join(HUMAN3D_DIR, 'model_output'))
    except:
        pass
    finally:
        os.mkdir(os.path.join(HUMAN3D_DIR, 'model_output')) 
    
    try: 
        shutil.rmtree(os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()), 'model_output'))
    except:
        pass
    
    try:
        os.remove(HUMAN3D_DIR + '\\data\\human_proportions.json')
    except:
        pass
    
    try:
        os.remove(HUMAN3D_DIR + '\\human_proportions.json')
    except:
        pass