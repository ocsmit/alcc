### Automated Landcover Classification arcpy Function

**Author: Owen Smith, IESA, University of North Georgia**

Parameters: 
* `landsat_dir 'str':` Input landsat data directory.
* `out_dir: 'str':` Directory where all outputs will be saved.
* `soil_brightness=0.5 'int':` Soil brightness factor for SAVI calculation.

Final output `out_dir/ALCC.tif`

Citations: 
- Gašparović, M., Zrinjski, M., & Gudelj, M. (2019). Automatic cost-effective 
  method for land cover classification (ALCC). Computers, Environment and Urban 
  Systems, 76, 1-10.