class cf(): # common functions
    
    MAIN_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
    JOINTS_MAP = ['Nose', 'Neck', 'RShoulder', 'RElbow' ,'RWrist', 'LShoulder',
               'LElbow', 'LWrist', 'MidHip', 'RHip', 'RKnee', 'RAnkle', 'LHip',
               'LKnee', 'LAnkle', 'REye', 'LEye', 'REar', 'LEar', 'LBigToe',
               'LSmallToe', 'LHeel', 'RBigToe', 'RSmallToe', 'RHeel']
    
    @staticmethod
    def parse_pose_25(Dir):
        f = open(Dir)
        data = json.load(f)
        arr = data['people'][0]['pose_keypoints_2d']

        Dict = {}
        for i in range(25):
            j=i*3
            Dict[cf.JOINTS_MAP[i]] = [arr[j], 1-arr[j+1], arr[j+2]]

        return Dict

    @staticmethod
    def load_frames_pose(Dir_pose = '\\frames\\pose\\'):     
        list_json_raw = listdir(cf.MAIN_DIR + Dir_pose)
        list_json = [('frame' + str(i+1) + '_keypoints.json') for i in range(len(list_json_raw)-1) if (str(list_json_raw[i]))[-4:] == "json"]
        frames = []
        for file_name in list_json:
            if cf.people_count_in_file(cf.MAIN_DIR + Dir_pose + file_name) == 1:
                frames.append(cf.parse_pose_25(cf.MAIN_DIR + Dir_pose + file_name))
            else:
                frames.append(frames[-1])

        f = open(cf.MAIN_DIR + Dir_pose + '\\my_fps.txt')
        fps = f.read()
        fps = float(fps)
        f.close()

        cf.fix_unseen_joints(frames)

        return frames, fps
    
    @staticmethod
    def people_count_in_file(Dir):
        f = open(Dir)
        data = json.load(f)
        arr = data['people']
        return len(arr)
    

    @staticmethod
    def fix_unseen_joints(frames):
        # TODO: make it more general
        for i in range(len(frames)):
            for joint in cf.JOINTS_MAP:
                if frames[i][joint][-1] == 0:
                    frames[i][joint] = frames[i-1][joint]
                    frames[i][joint][-1] = 0
        return frames

    @staticmethod
    def getAngle_2pts(p1, p2, degree=False):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle = math.atan2(dy, dx)

        if degree:
            angle = math.degrees(angle)
            
        return angle

    @staticmethod
    def getDistance_2pts(p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    @staticmethod
    def getDepthAngle(L1, L2, degree=False):
        if L2/L1 > 1:
            return 0
        
        angle = math.acos(L2/L1)
        if degree:
            angle = math.degrees(angle)

        return angle