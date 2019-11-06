from pixell import enmap, enplot, curvedsky, utils
from soapack import interfaces as soint
import os
from sandbox import misc
import numpy as np
from subprocess import Popen, PIPE
import json
from PIL import Image

# disable warning 
Image.MAX_IMAGE_PIXELS = None

overwrite = False
downgrade = 1
tilesize = 675

gdal2tiles_dir = '/mnt/home/dhan/workspace/gdal2tiles-leaflet'
output_dir = "/mnt/ceph/users/dhan/images"
output_path = lambda x: os.path.join(output_dir, x)

DM = soint.models['act_mr3'](calibrated=False)
patches = DM.get_psa_indexes()
patches = [patch for patch in patches if 'cmb_pa2_f150' in patch]

# make raw images
misc.create_dir(output_path('raw'))
for psa in patches:
    print("processing {}".format(psa))
    season, patch, array, freq = psa.split('_')
    array_freq = '{}_{}'.format(array, freq)
    fshape, fwcs = enmap.fullsky_geometry(0.5*utils.arcmin)

    misc.create_dir(output_path('raw/ivars'))
    ivar_file = output_path("raw/ivars/{}_ivar_gray.png".format(psa))
    if not os.path.exists(ivar_file) or overwrite:
        ivar = DM.get_coadd_ivar(season, patch, array_freq)
        ivar = enmap.downgrade(enmap.extract(ivar, fshape, fwcs),2)

        eplots = enplot.plot(ivar, color='gray', downgrade=downgrade, grid=False, mask=0)
        for eplot in eplots:
            enplot.write(ivar_file, eplot)

        del eplots
        del ivar

    misc.create_dir(output_path("raw/raw"))
    cmb_file_temp = output_path("raw/raw/%s_{}_data_planck.png"%(psa))
    if not os.path.exists(cmb_file_temp.format("U")) or overwrite:
        emaps = DM.get_coadd(season, patch, array_freq, srcfree=False, ncomp=None)
        emaps = enmap.downgrade(enmap.extract(emaps, fshape, fwcs),2)
        eplots = enplot.plot(emaps, downgrade=downgrade, grid=False)

        for i, cmb_idx in enumerate(['I','Q','U']):
            enplot.write(cmb_file_temp.format(cmb_idx), eplots[i])

        del eplots, emaps


    if not os.path.exists(cmb_file_temp.format("B")) or overwrite:
        continue
        emaps = DM.get_coadd(season, patch, array_freq, srcfree=False, ncomp=None)
        sshape, swcs = emaps.shape, emaps.wcs
        lmax = 8000
        alms = curvedsky.map2alm(emaps, lmax=lmax, spin=[0,2])
        emaps = curvedsky.alm2map(alms, enmap.zeros(sshape, swcs), spin=[0,2])
        emaps = enmap.downgrade(enmap.extract(emaps, fshape, fwcs),2)
        Image.MAX_IMAGE_PIXELS = None
        eplots = enplot.plot(emaps[1:,...], downgrade=downgrade, grid=False)

        for i, cmb_idx in enumerate(['E', 'B']):
            enplot.write(cmb_file_temp.format(cmb_idx), eplots[i])

        del alms, emaps, eplots

# make tiles

# make raw images
misc.create_dir(output_path('tiles'))
for psa in patches:
    print("processing {}".format(psa))
    season, patch, array, freq = psa.split('_')
    array_freq = '{}_{}'.format(array, freq)

    #ivar = DM.get_coadd_ivar(season, patch, array_freq)
    #shape, wcs = ivar.shape, ivar.wcs
    
    ivar_file = output_path("raw/ivars/{}_ivar_gray.png".format(psa)) 
    width, height = Image.open(ivar_file).size

    zfact = int(np.ceil(np.log2(max(width, height)/tilesize)))
    print(zfact)
    dgshape = [width, height]
    

    tile_path = lambda x, y, z: os.path.join(output_path('tiles'), x, y, z)
    misc.create_dir(output_path('tiles/ivars'))
    misc.create_dir(tile_path('ivars', psa, ''))

    check_file = tile_path('ivars', psa, 'finished.txt')
    if not os.path.exists(check_file) or overwrite:
        ivar_file = output_path("raw/ivars/{}_ivar_gray.png".format(psa)) 
        command = ['python', os.path.join(gdal2tiles_dir,'gdal2tiles.py'), '-l' ,'-praster', '-z0-%d'%zfact, '-wnone', ivar_file, tile_path('ivars', psa, '')]  
        print(command)
        process = Popen(command, stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        meta = {}
        meta['shape'] = dgshape
        meta['zoom'] = [0,zfact]
        meta['tilesize'] = tilesize
        if exit_code == 0: 
            with open(tile_path('ivars', psa, 'meta.json'), 'w') as outfile:
                json.dump(meta, outfile)
            open(check_file, 'a').close()
    
    misc.create_dir(output_path("tiles/raw"))
    misc.create_dir(tile_path('raw', psa, ''))
    check_file = tile_path('raw', psa, 'U/finished.txt')
    if not os.path.exists(check_file) or overwrite:
        cmb_file = output_path("raw/raw/%s_{}_data_planck.png"%psa) 
        for i, cmb_idx in enumerate(['I','Q','U']):
            temp_dir = tile_path('raw', psa, cmb_idx)
            command = ['python', os.path.join(gdal2tiles_dir,'gdal2tiles.py'), '-l' ,'-praster', '-z0-%d'%zfact, '-wnone', 
                    cmb_file.format(cmb_idx), temp_dir]  
            print(command)

            process = Popen(command, stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            meta = {}
            meta['shape'] = dgshape
            meta['zoom'] = [0,zfact]
            meta['tilesize'] = tilesize
            if exit_code == 0: 
                with open(tile_path('raw', psa, 'meta.json'), 'w') as outfile:
                    json.dump(meta, outfile)
            open(tile_path('raw', psa, '{}/finished.txt'.format(cmb_idx)), 'a').close()
        
