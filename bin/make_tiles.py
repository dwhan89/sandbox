from pixell import enmap
from soapack import interfaces as soint
import os

patches = soint.models['act_mr3']()
output_dir = "/mnt/ceph/users/dhan/images"
output_path = lambda x: os.path.join(output_dir, x)

for psa in patches:
    season, patch, array, freq = psa.split('_')



