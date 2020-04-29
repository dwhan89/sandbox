##
#  miscellenous scripts used throughout the code
##
import os
import numpy as np


def read_bin_edges(bin_file, skiprows=0):
    assert(os.path.exists(bin_file))
    (lower, upper, center) = np.loadtxt(bin_file, skiprows=skiprows, unpack=True)
    return np.concatenate((lower[0:1], upper))


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise TypeError("Can't convert 'str' object to 'boolean'")


def create_dir(path_to_dir):
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

def create_dict(*idxes):
    height  = len(idxes)
    output = {}

    stack  = []
    stack.append(output)

    for depth in range(height):
        stack_temp = []
        while len(stack) > 0:
            cur_elmt = stack.pop()
            for idx in idxes[depth]:
                cur_elmt[idx] = {}
                stack_temp.append(cur_elmt[idx])
        stack = stack_temp

    return output

def is_empty(s):
    return True if (s is None) or (len(s) == 0) else False

