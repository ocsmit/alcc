import arcpy
from arcpy.sa import *
import os
from glob import glob


def alcc(landsat_dir, out_dir, soil_brightness=0.5):
    arcpy.env.overwriteOutput = True
    arcpy.env.mask = None

    blue_path = glob(landsat_dir + "/*B2*")
    green_path = glob(landsat_dir + "/*B3*")
    red_path = glob(landsat_dir + "/*B4*")
    nir_path = glob(landsat_dir + "/*B5*")
    swir1_path = glob(landsat_dir + "/*B6*")
    swir2_path = glob(landsat_dir + "/*B7*")
    tir_path = glob(landsat_dir + "/*B10*")

    # Read as rasters
    blue = Raster(blue_path)
    green = Raster(green_path)
    red = Raster(red_path)
    nir = Raster(nir_path)
    swir1 = Raster(swir1_path)
    swir2 = Raster(swir2_path)
    tir = Raster(tir_path)

    # Output classifications
    savi_out = out_dir + "SAVI.tif"
    SAVI = Float(((nir - red) / (nir + red + soil_brightness)) *
                 (1 + soil_brightness))
    SAVI.save(savi_out)

    aweish_out = out_dir + "AWEIsh.tif"
    AWEIsh = Float((blue + 2.5 * green - 1.5 * (nir + swir1) - 0.25 * swir2) /
                   (blue + green + nir + swir1 + swir2))
    AWEIsh.save(aweish_out)

    ebbi_out = out_dir + "EBBI.tif"
    EBBI = Float(swir1 - nir / 10 * (SquareRoot(swir1 + tir)))
    EBBI.save(ebbi_out)

    # Water
    class_aweish = out_dir + "class_AWEIsh.tif"
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
    savi_nowater = "%s/SAVI_nw.tif" % out_dir
    savi_raster = arcpy.ia.Plus(savi_out, aweish_land)
    savi_raster.save(savi_nowater)

    class_savi = out_dir + "class_NDVI.tif"
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(
        savi_nowater, 6, 2, 2, None)
    iso_unsupervised.save(class_savi)

    low_veg = "%s/low_veg.tif" % out_dir
    lowveg_raster = arcpy.sa.ExtractByAttributes(class_savi, "Value = 3")
    lowveg_raster.save(low_veg)

    high_veg = "%s/high_veg.tif" % out_dir
    highveg_raster = arcpy.sa.ExtractByAttributes(class_savi, "Value > 3")
    highveg_raster.save(high_veg)

    savi_nv = "%s/SAVI_nv.tif" % out_dir
    noveg_raster = arcpy.sa.ExtractByAttributes(class_savi, "Value < 3")
    noveg_raster.save(savi_nv)

    # Bare earth and built up
    ebbi_only = "%s/EBBI_only.tif" % out_dir
    EBBI_raster = arcpy.ia.Plus(ebbi_out, savi_nv)
    EBBI_raster.save(ebbi_only)

    class_ebbi = out_dir + "class_EBBI.tif"
    iso_unsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(ebbi_only,
                                                                     6, 2, 2,
                                                                     None)
    iso_unsupervised.save(class_ebbi)

    built_up = "%s/built_up.tif" % out_dir
    builtup_raster = arcpy.sa.ExtractByAttributes(class_ebbi, "Value <= 3")
    builtup_raster.save(built_up)

    barren = "%s/barren.tif" % out_dir
    barren_raster = arcpy.sa.ExtractByAttributes(class_ebbi, "Value > 3")
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

    arcpy.Delete_managment(water, aweish_land, savi_nowater, high_veg,
                           low_veg, savi_nv, barren, built_up, ebbi_only)

    print('Completed.')