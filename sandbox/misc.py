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


def progress(count, total, status=''):
    # adoped from https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    bar_len = 60
    percents = 0
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    print('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
