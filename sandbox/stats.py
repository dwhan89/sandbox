#-
# stats.py
#-
#
from . import  mpi, config
import numpy as np

class STATS(object):

    def __init__(self, stat_identifier=None, output_dir =  None, overwrite=False, enable_batch=False, tag = 3235):
        self.output_dir  = output_dir
        self.batch_dir   = os.path.join(self.output_dir, batch_dir_name)
        if mpi.rank == 0 :
            print("[STATS] output_dir is %s" %self.output_dir)
            os.makedirs(self.output_dir, exist_ok=True)
        mpi.barrier()

        file_name        = "stats.pkl" if not stat_identifier else "stats_%s.pkl" %stat_identifier

        self.output_file  = os.path.join(self.output_dir, file_name)
        self.storage      = {}
        self.stats        = {}
        self.tag          = tag # can this be randomly assigned 
        try:
            assert(not overwrite)
            self.storage = pickle.load(open(self.output_file, 'r'))
            if mpi.rank == 0: print("[STATS] loaded %s" %self.output_file)
        except:
            if mpi.rank == 0: print("[STATS] starting from scratch")

    def add_data(self, data_key, data_idx, data, safe=False):
        if not self.storage.has_key(data_key): self.storage[data_key] = {}

        if self.storage[data_key].has_key(data_idx) and safe:
            raise ValueError("[STATS] already have %s" %((data_key,data_idx)))
        else:
            self.storage[data_key][data_idx] = data

    def collect_data(self, dest=0):
        print("[STATS] collecting data")

        if mpi.is_mpion():
            mpi.transfer_data(self.storage, self.tag, dest=dest, mode='merge')
        self.tag += 1

    def has_data(self, data_key, data_idx):
        has_data = self.storage.has_key(data_key)
        return has_data if not has_data else self.storage[data_key].has_key(data_idx)

    def reload_data(self):
        ### passing all data through mpi is through. save it and reload it
        try:
            self.storage = pickle.load(open(self.output_file, 'r'))
            if mpi.rank == 0: print("[STATS] loaded %s" %self.output_file)
        except:
            if mpi.rank == 0: print("[STATS] failed to reload data")

    def save_data(self, root=0, reload_st=True):
        self.collect_data()

        if mpi.rank == root:
            print("[STATS] saving %s from root %d" %(self.output_file, root))
            with open(self.output_file, 'w') as handle:
                pickle.dump(self.storage, handle)
        else: pass
        mpi.barrier()
        if reload_st: self.reload_data()

    def get_stats(self, subset_idxes=None):
        self.save_data(reload_st=True)

        print("calculating stats")
        ret = {}
        for key in self.storage.keys():
            if subset_idxes is None:
                ret[key] = stats(np.array(self.storage[key].values()))
            else:
                ret[key] = stats(np.array(self.get_subset(subset_idxes, key, False).values()))

        self.stats = ret
        return ret

    def purge_data(self, data_idx, data_key=None):
        self.collect_data()

        def _purge(data_key, data_idx):
            print("[STATS] purging %s %d" %(data_idx, data_key))
            del self.storage[data_key][data_idx]

        if mpi.rank == 0:
            if data_key is not None:
                _purge(data_key, data_idx)
            else:
                for data_key in self.storage.keys():
                    _purge(data_key, data_idx)

        self.reload_data()

    def get_subset(self, data_idxes, data_key=None, collect_data=False):
        if collect_data: self.collect_data()

        def _collect_subset(data_key, data_idxes):
            return dict((k, v) for k, v in self.storage[data_key].iteritems() if k in data_idxes)

        ret = {}
        if data_key is not None:
            ret = _collect_subset(data_key, data_idxes)
        else:
            for data_key in self.storage.keys():
                ret[data_key] = _collect_subset(data_key, data_idxes)

        return ret

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

def chisq(obs, exp, cov_input, ddof=None, sidx=None, eidx=None, inv_corr=1.0):
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

    print(inv_corr)
    cov_inv = np.linalg.pinv(cov)*inv_corr
    chisq = np.dot(cov_inv, diff)
    chisq = np.dot(diff.T, chisq)

    if ddof is None: ddof = len(diff)
    p     = chi2.sf(chisq, ddof)

    return(chisq, p)

def reduced_chisq(obs, exp, cov, ddof_cor=0., sidx=None, eidx=None, inv_corr=1.):
    if sidx is None: sidx = 0
    if eidx is None: eidx = len(obs)
    obs = obs[sidx:eidx]
    exp = exp[sidx:eidx]
    cov = cov[sidx:eidx, sidx:eidx]

    ddof     = len(obs)# ddof
    ddof_cor = float(ddof_cor)
    ddof     = ddof - ddof_cor

    _chisq, p = chisq(obs,exp,cov,ddof, sidx=None, eidx=None, inv_corr=inv_corr)
    rchisq    = _chisq / ddof
    print("DDOF: ",ddof)
    return(rchisq, p)


class BINNER(object):
    def __init__(self, bin_edges, lmax=None):

        lmax      = int(np.max(bin_edges) if lmax is None else lmax)
        assert(lmax >= 0.)

        bin_edges    = bin_edges.astype(np.int)
        bin_edges[0] = 2

        bin_lower      = bin_edges[:-1].copy()
        bin_lower[1:] += 1
        bin_upper      = bin_edges[1:].copy()

        bin_upper = bin_upper[np.where(bin_upper <= lmax)]
        bin_lower = bin_lower[:len(bin_upper)]
        bin_lower = bin_lower[np.where(bin_lower <= lmax)]

        self.lmax       = lmax
        self.bin_edges  = bin_edges
        self.bin_lower  = bin_lower
        self.bin_upper  = bin_upper
        self.bin_center = (bin_lower + bin_upper)/2.
        self.bin_sizes  = bin_upper - bin_lower + 1
        self.nbin       = len(bin_lower)

        assert((self.bin_sizes > 0)).all()


    def bin(self, l, cl):
        lbin  = self.bin_center
        clbin = np.zeros(self.nbin)
        for idx in range(0, self.nbin):
            low_lim , upp_lim = (self.bin_lower[idx], self.bin_upper[idx])

            loc   = np.where((l >= low_lim) & (l <= upp_lim))
            clbin[idx] = cl[loc].mean()

        return (lbin, clbin)

