from pixell import enmap, enplot
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
            eplot.write(ivar_file, eplot)

        del eplots
    del ivar

    #emap = DM.get_coadd(season, patch, array_freq, srcfree=False, ncomp=None)
    #eplots =