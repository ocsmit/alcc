################################################################################
# Title: Automated Landcover Classification Function                           #
# Author: Owen Smith                                                           #
# License: GNU v3.0                                                            #
# Email: ocsmit7654@ung.edu                                                    #
################################################################################

import arcpy
from arcpy.sa import *
import os
from glob import glob


def alcc(landsat_dir, out_dir):
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
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

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
    arvi_out = "%s/ARVI.tif" % out_dir
    arvi = Float((nir - (2 * red) + blue) / nir + (2 * red) + blue)
    arvi.save(arvi_out)

    aweish_out = "%s/AWEIsh.tif" % out_dir
    AWEIsh = Float((blue + 2.5 * green - 1.5 * (nir + swir1) - 0.25 * swir2) /
                   (blue + green + nir + swir1 + swir2))
    AWEIsh.save(aweish_out)

    ebbi_out = "%s/EBBI.tif" % out_dir
    EBBI = Float(swir1 - nir / 10 * (SquareRoot(swir1 + tir)))
    EBBI.save(ebbi_out)

    # Water
    class_aweish = "%s/class_AWEIsh.tif" % out_dir
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(aweish_out,
                                                                     6, 2, 2,
                                                                     None)
    iso_unsupervised.save(class_aweish)

    water = "%s/water.tif" % out_dir
    aweish_land = "%s/AWEIsh_land.tif" % out_dir

    water_raster = arcpy.sa.ExtractByAttributes(class_aweish, "Value = 6")
    water_raster.save(water)
    land_raster = arcpy.sa.ExtractByAttributes(class_aweish, "Value < 6")
    land_raster.save(aweish_land)
    land_raster = arcpy.sa.Reclassify(aweish_land, "Value",
                                      "1 0;2 0;3 0;4 0;5 0", "DATA")
    land_raster.save(aweish_land)

    # Vegetation
    arvi_nowater = "%s/ARVI_nw.tif" % out_dir
    arvi_raster = arcpy.ia.Plus(arvi_out, aweish_land)
    arvi_raster.save(arvi_nowater)

    class_arvi = "%s/class_ARVI.tif" % out_dir
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(
        arvi_nowater, 5, 2, 2, None)
    iso_unsupervised.save(class_arvi)

    low_veg = "%s/low_veg.tif" % out_dir
    lowveg_raster = arcpy.sa.ExtractByAttributes(class_arvi, "Value = 2")
    lowveg_raster.save(low_veg)

    high_veg = "%s/high_veg.tif" % out_dir
    highveg_raster = arcpy.sa.ExtractByAttributes(class_arvi, "Value = 1")
    highveg_raster.save(high_veg)

    arvi_nv = "%s/arvi_nv.tif" % out_dir
    noveg_raster = arcpy.sa.ExtractByAttributes(class_arvi, "Value > 2")
    noveg_raster.save(arvi_nv)

    # Bare earth and built up
    ebbi_only = "%s/EBBI_only.tif" % out_dir
    EBBI_raster = arcpy.ia.Plus(ebbi_out, arvi_nv)
    EBBI_raster.save(ebbi_only)

    class_ebbi = "%s/class_EBBI.tif" % out_dir
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(ebbi_only,
                                                                     3, 2, 2,
                                                                     None)
    iso_unsupervised.save(class_ebbi)

    built_up = "%s/built_up.tif" % out_dir
    builtup_raster = arcpy.sa.ExtractByAttributes(class_ebbi, "Value = 3")
    builtup_raster.save(built_up)

    barren = "%s/barren.tif" % out_dir
    barren_raster = arcpy.sa.ExtractByAttributes(class_ebbi, "Value < 3")
    barren_raster.save(barren)

    cst = 1
    water_re = "%s/water_re.tif" % out_dir
    water_reclass = Con(water, cst)
    water_reclass.save(water_re)
    print("Water: 1")

    cst = 2
    low_veg_re = "%s/low_veg_re.tif" % out_dir
    lowveg_reclass = Con(low_veg, cst)
    lowveg_reclass.save(low_veg_re)
    print("Low vegetation: 2")

    cst = 3
    high_veg_re = "%s/high_veg_re.tif" % out_dir
    highveg_reclass = Con(high_veg, cst)
    highveg_reclass.save(high_veg_re)
    print("High vegetation: 3")

    cst = 4
    built_up_re = "%s/built_up_re.tif" % out_dir
    builtup_reclass = Con(built_up, cst)
    builtup_reclass.save(built_up_re)
    print("Built-up: 4")

    cst = 5
    barren_re = "%s/barren_two_re.tif" % out_dir
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

    del_rast = [water, aweish_land, arvi_nowater, high_veg, low_veg, arvi_nv,
                barren, built_up, ebbi_only]
    for i in del_rast:
        arcpy.Delete_management(i)
    print('Completed.')
