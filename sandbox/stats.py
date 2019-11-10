# -
# stats.py
# -
#

import numpy as np


def stats(data, axis=0, ddof=1.):
    datasize = data.shape
    mean = np.mean(data, axis=axis)
    cov = np.cov(data.transpose(), ddof=ddof)
    cov_mean = cov / float(datasize[0])
    corrcoef = np.corrcoef(data.transpose())
    std = np.std(data, axis=axis, ddof=ddof)  # use the N-1 normalization
    std_mean = std / np.sqrt(datasize[0])

    return {'mean': mean, 'cov': cov, 'corrcoef': corrcoef, 'std': std, 'datasize': datasize \
        , 'std_mean': std_mean, 'cov_mean': cov_mean}
