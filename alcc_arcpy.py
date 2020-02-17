#-------------------------------------------------------------------------------
# Title: Automated Landcover Classification Function For arcpy
# Author: Owen Smith
# License: GNU v3.0
# Email: ocsmit7654@ung.edu
#-------------------------------------------------------------------------------

import arcpy    
from arcpy.sa import *
import os
from glob import glob


def alcc_arcpy(landsat_dir, out_dir, soil_brightness=0.5):
    '''
    landsat_dir 'str': Input landsat data directory.
    out_dir: 'str':  Directory where all outputs will be saved.

    final output 'out_dir/ALCC.tif'
    '''
    print('ALCC started.')
    arcpy.env.overwriteOutput = True
    arcpy.env.mask = None

    if not os.path.exists(landsat_dir):
        print('Input landsat directory does not exist.')
    if not os.path.exists('in_memory'):
        os.mkdir('in_memory')

    blue_path = glob(landsat_dir + "/*B2*")
    green_path = glob(landsat_dir + "/*B3*")
    red_path = glob(landsat_dir + "/*B4*")
    nir_path = glob(landsat_dir + "/*B5*")
    swir1_path = glob(landsat_dir + "/*B6*")
    swir2_path = glob(landsat_dir + "/*B7*")
    tir_path = glob(landsat_dir + "/*B10*")

    # Read as raster
    blue = Raster(blue_path[0])
    green = Raster(green_path[0])
    red = Raster(red_path[0])
    nir = Raster(nir_path[0])
    swir1 = Raster(swir1_path[0])
    swir2 = Raster(swir2_path[0])
    tir = Raster(tir_path[0])

    # Output classifications
    savi_out = "%s/SAVI.tif" % 'in_memory'
    SAVI = Float(((nir - red) / (nir + red + soil_brightness)) *
                 (1 + soil_brightness))
    SAVI.save(savi_out)
    
    aweish_out = "%s/AWEIsh.tif" % 'in_memory'
    AWEIsh = Float((blue + 2.5 * green - 1.5 * (nir + swir1) - 0.25 * swir2) /
                   (blue + green + nir + swir1 + swir2))
    AWEIsh.save(aweish_out)

    nbli_out = "%s/NBLI.tif" % 'in_memory'
    NBLI = Float(red - tir / red + tir)
    NBLI.save(nbli_out)

    # Water
    class_aweish = "%s/class_AWEIsh.tif" % 'in_memory'
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(aweish_out,
                                                                     8, 2, 2,
                                                                     None)
    iso_unsupervised.save(class_aweish)

    water = "%s/water.tif" % 'in_memory'
    aweish_land = "%s/AWEIsh_land.tif" % 'in_memory'

    water_raster = arcpy.sa.ExtractByAttributes(class_aweish, "Value = 8")
    water_raster.save(water)
    land_raster = arcpy.sa.ExtractByAttributes(class_aweish, "Value < 8")
    land_raster.save(aweish_land)
    land_raster = arcpy.sa.Reclassify(aweish_land, "Value",
                                      "1 0;2 0;3 0;4 0;5 0;6 0;7 0", "DATA")
    land_raster.save(aweish_land)

    # Vegetation
    savi_nowater = "%s/SAVI_nw.tif" % 'in_memory'
    savi_raster = arcpy.ia.Plus(savi_out, aweish_land)
    savi_raster.save(savi_nowater)

    class_savi = "%s/class_SAVI.tif" % 'in_memory'
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(
        savi_nowater, 6, 2, 2, None)
    iso_unsupervised.save(class_savi)

    low_veg = "%s/low_veg.tif" % 'in_memory'
    lowveg_raster = arcpy.sa.ExtractByAttributes(class_savi, "Value = 3")
    lowveg_raster.save(low_veg)

    high_veg = "%s/high_veg.tif" % 'in_memory'
    highveg_raster = arcpy.sa.ExtractByAttributes(class_savi, "Value > 3")
    highveg_raster.save(high_veg)

    savi_nv = "%s/savi_nv.tif" % 'in_memory'
    noveg_raster = arcpy.sa.ExtractByAttributes(class_savi, "Value < 3")
    noveg_raster.save(savi_nv)

    noveg_raster = arcpy.sa.Reclassify(savi_nv, "Value", "2 0;1 0",
                                       "DATA")
    savi_nv = '%s/savi_nv.tif' % 'in_memory'
    noveg_raster.save(savi_nv)

    # Bare earth and built up
    nbli_only = "%s/NBLI_only.tif" % 'in_memory'
    NBLI_raster = arcpy.ia.Plus(nbli_out, savi_nv)
    NBLI_raster.save(nbli_only)

    class_nbli = "%s/class_NBLI.tif" % 'in_memory'
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(nbli_only,
                                                                     6, 2, 2,
                                                                     None)
    iso_unsupervised.save(class_nbli)

    built_up = "%s/built_up.tif" % 'in_memory'
    builtup_raster = arcpy.sa.ExtractByAttributes(class_nbli, "Value >= 3")
    builtup_raster.save(built_up)

    barren = "%s/barren.tif" % 'in_memory'
    barren_raster = arcpy.sa.ExtractByAttributes(class_nbli, "Value < 3")
    barren_raster.save(barren)

    cst = 1
    water_re = "%s/water_re.tif" % 'in_memory'
    water_reclass = Con(water, cst)
    water_reclass.save(water_re)
    print("Water: 1")

    cst = 2
    low_veg_re = "%s/low_veg_re.tif" % 'in_memory'
    lowveg_reclass = Con(low_veg, cst)
    lowveg_reclass.save(low_veg_re)
    print("Low vegetation: 2")

    cst = 3
    high_veg_re = "%s/high_veg_re.tif" % 'in_memory'
    highveg_reclass = Con(high_veg, cst)
    highveg_reclass.save(high_veg_re)
    print("High vegetation: 3")

    cst = 4
    built_up_re = "%s/built_up_re.tif" % 'in_memory'
    builtup_reclass = Con(built_up, cst)
    builtup_reclass.save(built_up_re)
    print("Built-up: 4")

    cst = 5
    barren_re = "%s/barren_two_re.tif" % 'in_memory'
    barren_reclass = Con(barren, cst)
    barren_reclass.save(barren_re)
    print("Barren: 5")

    print("Combining classes")
    arcpy.management.MosaicToNewRaster(
        [water_re, low_veg_re, high_veg_re, built_up_re, barren_re],
        out_dir,
        'ALCC.tif',
        None,
        "8_BIT_UNSIGNED",
        30,
        1,
        "LAST",
        "FIRST")

    print('Completed.')
