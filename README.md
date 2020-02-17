### Automated Landcover Classification using unsupervised classification methods

**Author: Owen Smith, IESA, University of North Georgia**

#### `alcc_arcpy(landsat_dir, out_dir, soil_brightness):` Runtime: ~2:15 minutes
* `landsat_dir 'str':` Input landsat data directory.
* `out_dir: 'str':` Directory where all outputs will be saved.
* `soil_brightness=0.5 'int':` Soil brightness factor for SAVI calculation.

Final output `out_dir/ALCC.tif`

Classification values still need tweaked.

Plans to implement scikit learn clustering with numpy arrays to replace arcgis unsupervised isocluster.

#### `alcc_foss:`
* WIP

Citations: 
- Gašparović, M., Zrinjski, M., & Gudelj, M. (2019). Automatic cost-effective 
  method for land cover classification (ALCC). Computers, Environment and Urban 
  Systems, 76, 1-10.
