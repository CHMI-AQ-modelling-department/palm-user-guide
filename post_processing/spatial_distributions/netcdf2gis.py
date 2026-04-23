import numpy as np
from netCDF4 import Dataset
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta, timezone
from utils import *

plt.rc('text', usetex=False)
plt.rc('font', family='serif')

# Definitions
srid_palm=32633
srid_wgs84=4326
plot_folder = '/storage/home/gunes/palm/my.model.git/build/JOBS/my_carmine_prague/OUTPUT/thermal_comfort_indices/bio_utci_av_xy_joined'
# plt.ioff()                    # Switch turn off interactive plots

# define file
file = '/storage/home/gunes/palm/my.model.git/build/JOBS/my_carmine_prague/OUTPUT/JOINED/my_carmine_prague_av_xy'   # C_03m01_av_masked_N02_kcPM10
k_levels = [0]
fixed_ranges = [[None, None], ]
avg_axis = (0)
var_mods = [1.0, ]
variables = ['bio_utci*_xy'] #'bio_mrt*_xy', 'bio_perct*_xy', 'bio_pet*_xy']
colorbar_labels = ['Bio UTC / unit'] #'Bio mrt / unit', 'Bio perct / unit', 'Bio Pet / unit']
titles = ['Bio UTC'] #'Bio mrt', 'Bio perct', 'Bio Pet']

# file = '/home/reznicek/palm/output_diff/C_03m01_av_masked_N02_kcPM10'        # PATH
# k_levels = [0, 1, 2, 3] # average between levels                             # List of all level to be averaged
# fixed_ranges = [[+80, -80], ]                                                # List of pairs for data ranges, if None taken from min, max avg field
# avg_axis = (0, 1)                                                            # Axis to be average: 0..time, 1..z, 2..y, 3..x
# variables = ['kc_PM10'] #'bio_mrt*_xy', 'bio_perct*_xy', 'bio_pet*_xy']      # List of all variables
# var_mods = [1.0e9]   # modify variable range                                 # Variable multiplier
# colorbar_labels = [r'PM10 / $\mu$g / m3'] #'Bio mrt / unit', 'Bio perct / unit', 'Bio Pet / unit']   # Labels in Colorbar
# titles = ['PM10'] #'Bio mrt', 'Bio perct', 'Bio Pet']                                                # Title

# open file
nc = Dataset(file, 'r')

# read times
p_times = nc.variables['time'][:]
p_times_mask = ~p_times.mask
p_times = p_times[p_times_mask].data.squeeze()
p_times = [
    datetime.strptime(nc.origin_time, '%Y-%m-%d %H:%M:%S +00').astimezone(timezone.utc) + timedelta(seconds=int(nct))
    for nct in p_times]

origin_time_dt = datetime.strptime(nc.origin_time, '%Y-%m-%d %H:%M:%S +00').astimezone(timezone.utc)
avg_times_mask, avg_time_grid = palm_average(p_times, origin_time_dt)

# read x, y, lat, lon, transform
x, y = nc.variables['x'][:] , nc.variables['y'][:]
dx, dy = x[1] - x[0], y[1] - y[0]
x += nc.origin_x
y += nc.origin_y
X, Y = np.meshgrid(x, y)
transformer = Transformer.from_crs(CRS.from_user_input(srid_palm),
                                   CRS.from_user_input(srid_wgs84))
Xlat, Xlon = transformer.transform(X, Y)

# loop over variables
for var_name, colorbar_label, title, var_mod, fixed_range in zip(variables, colorbar_labels, titles, var_mods, fixed_ranges):
    print('Processing variable: {}'.format(var_name))
    for it in range(len(avg_times_mask)):
        if len(avg_times_mask[it]) == 0:
            continue
        print('Do averaging between {} and {}'.format(p_times[avg_times_mask[it][0]], p_times[avg_times_mask[it][-1]]))
        output_file = var_name.replace('\*','')
        asc_file = plot_folder + '/' + output_file + '_{}.asc'.format(it)
        png_file = plot_folder + '/' + output_file + '_{}.png'.format(it)

        var_data = np.squeeze(np.nanmean(nc.variables[var_name][avg_times_mask[it], k_levels, :, :], axis=avg_axis).data) * var_mod
        var_mask = nc.variables[var_name][0, 0, :, :].mask

        var_data[var_mask] = -9999.0
        dump2ascii(var_data, x, y, asc_file)

        var_data[var_mask] = np.nan

        fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(111)
        m = Basemap(projection='lcc', llcrnrlon=np.min(Xlon), llcrnrlat=np.min(Xlat), urcrnrlon=np.max(Xlon),
                    urcrnrlat=np.max(Xlat),
                    resolution='l',
                    lat_0=Xlat.mean(), lon_0=Xlon.mean(),
                    ax=ax)
        nx, ny = x.size, y.size

        lons = np.linspace(np.min(Xlon[int(1/4*nx)]), np.max(Xlon[int(4/5*nx)]), 3)
        lats = np.linspace(np.min(Xlat[int(1/4*ny)]), np.max(Xlat[int(4/5*ny)]), 3)
        m.drawmeridians(lons, labels=[0, 0, 0, 1], zorder=2, color='w')
        m.drawparallels(lats, labels=[1, 0, 0, 0], zorder=2, color='w')

        if fixed_range[0]:
            avg_max = fixed_range[0]
        else:
            avg_max = np.ceil(np.nanmax(var_data))

        if fixed_range[1]:
            avg_min = fixed_range[1]
        else:
            avg_min = np.floor(np.nanmin(var_data))
        avg_avg = np.nanmean(var_data)
        # norm = colors.TwoSlopeNorm(vmin=min([-0.001, avg_min]), vcenter=0,
        #                                    vmax=max([ 0.001, avg_max]))

        n_levs = 20
        if -avg_max != avg_min:
            avg_min, avg_max = -max([-avg_min, avg_max]), max([-avg_min, avg_max])
        bounds = np.linspace(avg_min, avg_max, n_levs)
        bound_ticks = np.linspace(avg_min, avg_max, n_levs - 1)
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)

        cmap = plt.get_cmap('bwr')
        cmap.set_bad('black', 1.)
        ax_2d = m.imshow(var_data, cmap=cmap, norm=norm,  # 'Spectral'),
                         origin='lower',
                         extent=[np.min(Xlon), np.max(Xlon), np.min(Xlat), np.max(Xlat)],
                         interpolation=None,
                         zorder=2)
        # current_cmap = plt.cm.get_cmap()
        # current_cmap.set_bad(color='black', -9999.0)

        ax.text(560, 520, r'$\uparrow$' + "\n N ", ha='center', fontsize=25, family='Arial', rotation=0)
        # $\u25b2$$\u25b2$
        m.drawmapscale(14.3932, 50.101, 14.3942, 50.101, 100, units='m', barstyle='fancy', zorder=4)

        fig.colorbar(ax_2d, label=colorbar_label, ticks=bound_ticks)
        avg_min, avg_max, avg_avg = np.nanmin(var_data), np.nanmax(var_data), np.nanmean(var_data)
        avg_range = 'Times: {} and {}'.format(p_times[avg_times_mask[it][0]].strftime('%m.%d %H:%M'), p_times[avg_times_mask[it][-1]].strftime('%m.%d %H:%M'))
        titlee = title + '\n' + 'min: {:.2f}, max: {:.2f}, avg: {:.2f}'.format(avg_min, avg_max, avg_avg) + '\n' + avg_range
        plt.title(titlee)
        fig.savefig(png_file, dpi=400)
