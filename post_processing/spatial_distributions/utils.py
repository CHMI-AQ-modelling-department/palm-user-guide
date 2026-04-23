import numpy as np
from pyproj import CRS, Transformer
from datetime import datetime, timedelta, timezone
import urllib

def palm_average(p_times, origin, avg_interval=3600):
    start_time = origin
    end_time = p_times[-1]
    difference = end_time - start_time
    time_diffs = int(difference.total_seconds() / avg_interval) + 2
    time_grid = [start_time + timedelta(seconds=n * int(avg_interval)) for n in range(time_diffs)]
    avg_time_mask = []
    for it in range(len(time_grid) - 1):
        avg_temp = []
        for i_temp, o_time in enumerate(p_times):
            if time_grid[it] < o_time <= time_grid[it + 1]:
                avg_temp.append(i_temp)
        avg_time_mask.append(avg_temp)

    return avg_time_mask, time_grid

def getWKT_PRJ(epsg_code):
    # access projection information
    wkt = urllib.request.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code))
    wkt = wkt.read().decode("utf-8")
    # remove spaces between charachters
    remove_spaces = wkt.replace(" ", "")
    # place all the text on one line
    output = remove_spaces.replace("\n", "")
    return output

def dump2ascii(var, x, y,
               asc_file,
               srid_palm=32633, srid_wgs84=4326):
    """ Function to dump data into ASCII format """
    acs_f = open(asc_file, 'w')
    # WRITE Header
    acs_f.write('NCOLS {}\n'.format(x.size))
    acs_f.write('NROWS {}\n'.format(y.size))
    acs_f.write('XLLCORNER {}\n'.format(x[0]))
    acs_f.write('YLLCORNER {}\n'.format(y[0]))
    cell_size = x[1] - x[0]
    acs_f.write('CELLSIZE {}\n'.format(cell_size))
    # acs_f.write('CELLSIZE -9999\n')
    acs_f.write('NODATA_VALUE -9999\n')
    for j in range(y.size - 1, -1, -1):
        acs_f.write(' '.join(map(str, list(var[j, :]))) + '\n')
    acs_f.close()

    """ CREATE .prj FILE """
    # create the .prj file
    prj = open(asc_file.replace('.asc', '.prj'), 'w')
    # call the function and supply the epsg code
    epsg = getWKT_PRJ(str(srid_palm))
    prj.write(epsg)
    prj.close()