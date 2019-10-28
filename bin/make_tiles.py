from pixell import enmap, enplot, curvedsky
from soapack import interfaces as soint
import os
from sandbox import misc

overwrite = False

output_dir = "/mnt/ceph/users/dhan/images"
output_path = lambda x: os.path.join(output_dir, x)

DM = soint.models['act_mr3'](calibrated=False)
patches = DM.get_psa_indexes()

for psa in patches:
    print("processing {}".format(psa))
    season, patch, array, freq = psa.split('_')
    array_freq = '{}_{}'.format(array, freq)

    ivar = DM.get_coadd_ivar(season, patch, array_freq)
    shape, wcs = ivar.shape, ivar.wcs

    misc.create_dir(output_path('ivars'))
    ivar_file = output_path("ivars/{}_ivar_gray.png".format(psa))
    if not os.path.exists(ivar_file) or overwrite:

        eplots = enplot.plot(ivar, color='gray', downgrade=2, grid=True, mask=0)
        for eplot in eplots:
            enplot.write(ivar_file, eplot)

        del eplots
    del ivar

    misc.create_dir(output_path("data"))
    cmb_file_temp = output_path("data/%s_{}_data_color.png"%(psa))

    if not os.path.exists(cmb_file_temp.format("U")) or overwrite:
        emaps = DM.get_coadd(season, patch, array_freq, srcfree=False, ncomp=None)
        eplots = enplot.plot(emaps, downgrade=2, grid=True, mask=0)

        for i, cmb_idx in enumerate(['I','Q','U']):
            enplot.write(cmb_file_temp.format(cmb_idx), eplots[i])

        del eplots, emaps


    if not os.path.exists(cmb_file_temp.format("B")) or overwrite:
        emaps = DM.get_coadd(season, patch, array_freq, srcfree=False, ncomp=None)
        sshape, swcs = emaps.shape, emaps.wcs

        lmax = 8000
        alms = curvedsky.map2alm(emaps, lmax=lmax, spin=[0,2])
        emaps = curvedsky.alm2map(alms, enmap.zeros(sshape, swcs), spin=[0,2])
        eplots = enplot.plot(emaps[1:,...], downgrade=2, grid=True)

        for i, cmb_idx in enumerate(['E', 'B']):
            enplot.write(cmb_file_temp.format(cmb_idx), eplots[i])

        del alms, emaps, eplots

