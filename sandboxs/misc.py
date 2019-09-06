##
#  miscellenous scripts used throughout the code
##
import os

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise TypeError("Can't convert 'str' object to 'boolean'")

def create_dir(path_to_dir):
    ''' check wether the directory already exists. if not, create it '''
    if not os.path.isdir(path_to_dir):
        os.makedirs(path_to_dir)
        exit = 0
    else:
        exit = 1

    return exit
