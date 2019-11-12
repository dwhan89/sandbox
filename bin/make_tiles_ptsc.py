from pixell import enmap, enplot, curvedsky, utils
from soapack import interfaces as soint
import os
from sandbox import misc
import numpy as np
from subprocess import Popen, PIPE
import json
from PIL import Image
from crush import catalog, visualize
import sys

# disable warning 
Image.MAX_IMAGE_PIXELS = None

overwrite = False
downgrade = 1
tilesize = 675

gdal2tiles_dir = '/mnt/home/dhan/workspace/gdal2tiles-leaflet'
output_dir = "/mnt/ceph/users/dhan/images"
output_path = lambda x: os.path.join(output_dir, x)
catalog_dir = '/mnt/home/dhan/workspace/crush/output/act_mr3'

HC = catalog.HierarchicalCatalog(catalog_dir)
structure = HC.load(greedy=True)
shape, wcs = enmap.fullsky_geometry(res=1.0*utils.arcmin)

vmax = max(np.max(HC.catalogs[1]['f150']['jy']), np.max(HC.catalogs[1]['f090']['jy']))
vmin = min(np.min(HC.catalogs[1]['f150']['jy']), np.min(HC.catalogs[1]['f090']['jy']))
cm_range = [vmin, vmax]

misc.create_dir(output_path('raw'))
misc.create_dir(output_path('raw/ptsc'))
for freq in structure.keys():
    for season in structure[freq].keys():
        ptsc_file = output_path("raw/ptsc/{}_{}.png".format(freq, season))
        if not os.path.exists(ptsc_file) or overwrite:
            img = visualize.draw_ellipse_from_catalog(HC.catalogs[2][freq][season], shape, wcs, cm_range=cm_range, use_cm=True, cm_style='seismic', width=4)
            img.save(ptsc_file) 

    ptsc_file = output_path("raw/ptsc/{}_{}.png".format(freq, 'merged'))
    if not os.path.exists(ptsc_file) or overwrite:
        img = visualize.draw_ellipse_from_catalog(HC.catalogs[1][freq], shape, wcs, cm_range=cm_range, use_cm=True, cm_style='seismic', width=4)
        img.save(ptsc_file) 

# make raw images
misc.create_dir(output_path('tiles'))
for freq in structure.keys():
    seasons = list(structure[freq].keys()) + ['merged']
    for season in seasons:
        tile_idx = "{}_{}".format(freq, season)
        ptsc_file = output_path("raw/ptsc/{}_{}.png".format(freq, season)) 
        width, height = Image.open(ptsc_file).size

        zfact = int(np.ceil(np.log2(max(width, height)/tilesize)))
        print(zfact)
        dgshape = [width, height]
    

        tile_path = lambda x, y, z: os.path.join(output_path('tiles'), x, y, z)
        misc.create_dir(output_path('tiles/ptsc'))
        misc.create_dir(tile_path('ptsc', tile_idx, ''))

        check_file = tile_path('ptsc', tile_idx, 'finished.txt')
        if not os.path.exists(check_file) or overwrite:
            ptsc_file = output_path("raw/ptsc/{}.png".format(tile_idx)) 
            command = ['python', os.path.join(gdal2tiles_dir,'gdal2tiles.py'), '-l' ,'-praster', '-z0-%d'%zfact, '-wnone', ptsc_file, tile_path('ptsc', tile_idx, '')]  
            print(command)
            process = Popen(command, stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            meta = {}
            meta['shape'] = dgshape
            meta['zoom'] = [0,zfact]
            meta['tilesize'] = tilesize
            if exit_code == 0:  
                for i in np.arange(zfact+1).astype(int):
                    os.rename(tile_path('ptsc', tile_idx, str(i)), tile_path('ptsc', tile_idx, str(int(i-zfact))))
                with open(tile_path('ptsc', tile_idx, 'meta.json'), 'w') as outfile:
                    json.dump(meta, outfile)
            open(check_file, 'a').close()

        else:
            pass
        
    tile_idx = "{}".format(freq)
    dust_file = output_path("raw/dust/{}.png".format(freq)) 
    width, height = Image.open(dust_file).size
    print(width, height)
    zfact = int(np.ceil(np.log2(max(width, height)/tilesize)))
    print(zfact)
    dgshape = [width, height]


    tile_path = lambda x, y, z: os.path.join(output_path('tiles'), x, y, z)
    misc.create_dir(output_path('tiles/dust'))
    misc.create_dir(tile_path('dust', tile_idx, ''))

    check_file = tile_path('dust', tile_idx, 'finished.txt')
    if not os.path.exists(check_file) or overwrite:
        ptsc_file = output_path("raw/dust/{}.png".format(tile_idx)) 
        command = ['python', os.path.join(gdal2tiles_dir,'gdal2tiles.py'), '-l' ,'-praster', '-z0-%d'%zfact, '-wnone', dust_file, tile_path('dust', tile_idx, '')]  
        print(command)
        process = Popen(command, stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        meta = {}
        meta['shape'] = dgshape
        meta['zoom'] = [0,zfact]
        meta['tilesize'] = tilesize
        if exit_code == 0:  
            for i in np.arange(zfact+1).astype(int):
                os.rename(tile_path('dust', tile_idx, str(i)), tile_path('ptsc', tile_idx, str(int(i-zfact))))
            with open(tile_path('dust', tile_idx, 'meta.json'), 'w') as outfile:
                json.dump(meta, outfile)
        open(check_file, 'a').close()

    else:
        pass
    
