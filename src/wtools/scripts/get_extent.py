#!/usr/bin/env python

import sys
import gdal
import osr

if __name__ == '__main__':
    filename = sys.argv[1]

    dataset = gdal.Open(filename, gdal.GA_ReadOnly)

    if dataset is None:
        print("failed - unable to open.")
        sys.exit(1)

    transform = dataset.GetGeoTransform(can_return_null = True)
    if transform is None:
        print("failed - no tranform")
        sys.exit(1)

    nx = dataset.RasterXSize
    ny = dataset.RasterYSize
    xmin = transform[0]
    ymin = transform[3]
    xmax = transform[0] + transform[1] * nx
    ymax = transform[3] + transform[5] * ny

    # flip coordinates, actually this should not be required and dx, dy or CRS should be passed instead
    xmin2 = min(xmin, xmax)
    xmax2 = max(xmin, xmax)
    ymin2 = min(ymin, ymax)
    ymax2 = max(ymin, ymax)
    
    print('{0} {1} {2} {3}'.format(xmin2, ymin2, xmax2, ymax2))
