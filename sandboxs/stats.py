#-
# stats.py
#-
#

import numpy as np

def stats(data, axis=0, ddof=1.):
    datasize = data.shape
    mean     = np.mean(data, axis=axis)
    cov      = np.cov(data.transpose(), ddof=ddof)
    cov_mean = cov/ float(datasize[0])
    corrcoef = np.corrcoef(data.transpose())
    std      = np.std(data, axis=axis, ddof=ddof) # use the N-1 normalization
    std_mean = std/ np.sqrt(datasize[0])

    return {'mean': mean, 'cov': cov, 'corrcoef': corrcoef, 'std': std, 'datasize': datasize\
            ,'std_mean': std_mean, 'cov_mean': cov_mean}

def chisq(obs, exp, cov_input, ddof=None, sidx=None, eidx=None):
    from scipy.stats import chi2
    diff  = obs-exp if not (exp == 0.).all() else obs.copy()
    cov  = cov_input.copy()

    if sidx is None: sidx = 0
    if eidx is None: eidx = len(diff)
    diff = diff[sidx:eidx]
    cov  = cov[sidx:eidx, sidx:eidx]

    norm = np.mean(np.abs(cov))
    cov  /= norm
    diff /= np.sqrt(norm)

    chisq = np.dot(np.linalg.pinv(cov), diff)
    chisq = np.dot(diff.T, chisq)

    if ddof is None: ddof = len(diff)
    p     = chi2.sf(chisq, ddof)

    return(chisq, p)

def reduced_chisq(obs, exp, cov, ddof_cor=0., sidx=None, eidx=None):
    if sidx is None: sidx = 0
    if eidx is None: eidx = len(obs)
    obs = obs[sidx:eidx]
    exp = exp[sidx:eidx]
    cov = cov[sidx:eidx, sidx:eidx]

    ddof     = len(obs)# ddof
    ddof_cor = float(ddof_cor)
    ddof     = ddof - ddof_cor

    _chisq, p = chisq(obs,exp,cov,ddof, sidx=None, eidx=None)
    rchisq    = _chisq / ddof
    print("DDOF: ",ddof)
    return(rchisq, p)
