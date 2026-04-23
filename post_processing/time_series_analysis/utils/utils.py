import numpy as np
import pandas as pd
from math import floor
from netCDF4 import Dataset
from datetime import datetime, timedelta, timezone
from pyproj import CRS, Transformer
from suntime import Sun
import os
import glob

def get_time_grid_ticks(cfg):
    start_time = cfg.date_start #datetime.strptime(cfg.date_start, '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)
    end_time = cfg.date_end #datetime.strptime(cfg.date_end, '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)
    difference = end_time - start_time
    time_diffs = int(difference.total_seconds() / 3600) + 2

    time_grid = [start_time + timedelta(seconds=n * int(3600)) for n in range(time_diffs)]
    q = 0
    time_ticks = []
    time_ticks_loc = []
    for i in range(len(time_grid)):
        if time_grid[i].hour == 0:
            time_ticks.append(time_grid[i].strftime('%m-%d %H'))
            time_ticks_loc.append(q)
            q += 1
        elif time_grid[i].hour in [3, 6, 9, 12, 15, 18, 21]:
            time_ticks.append(time_grid[i].strftime('%H'))
            time_ticks_loc.append(q)
            q += 1
        else:
            pass
    return time_ticks, time_ticks_loc

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def findnearest(xlon, xlat, point):
    import scipy.spatial

    if len(xlon.shape) == 3:
        xlon = xlon[0]
        xlat = xlat[0]

    mytree = scipy.spatial.KDTree(list(zip(xlon.ravel(order='F'),
                                           xlat.ravel(order='F'))))
    dist, index = mytree.query(point)
    ncols = xlon.shape[0]

    y = index % ncols
    x = int(floor(index / ncols))

    return (x, y)

def read_station_loc(cfg, id, sep=';'):
    """ """
    df = pd.read_csv(cfg.observation_metadata, sep=sep)
    # selection station
    try:
        df_s = df[df['Station_ID'] == id]
    except:
        print('Unknown station id, exit')
        exit(1)
    lat, lon, height = df_s['Latitude'].iloc[0], df_s['Longitude'].iloc[0], df_s['Height_mAGL'].iloc[0]

    if np.isnan(height):
        height = 2.0

    return lat, lon, height


def read_station_concentrations(cfg, conc_id, id2, id, sep=';'):
    """ """
    df = pd.read_csv(cfg.observation_file_sensor, sep=sep)
    df['time'] = pd.to_datetime(df['dt_beg_utc'], format=cfg.datetime_formats.sensor).dt.tz_localize(timezone.utc)
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')
    df.index = df['time']


    # limit df by selected date
    df_s = df[(df.time >= cfg.date_start) &
              (df.time <= cfg.date_end)]

    # exit(1)

    # read all variables
    for var in conc_id.keys():
        try:
            if var == 'NO':
                var_id_no2 = cfg.variable_names.sensor['NO2'] + id2
                no2 = np.asarray(df_s[var_id_no2]) * cfg.units_conversion.sensor['NO2']
                aim_ratio = np.asarray(df_s['NO_NO2_ratio_Legerova'])
                no = no2 * aim_ratio
                conc_id[var][id + 'obs_data'] = no
                conc_id[var][id + 'obs_datetime'] = [time.to_pydatetime() for time in df_s['time']]
            elif var == 'NOx':
                var_id_no2 = cfg.variable_names.sensor['NO2'] + id2
                no2 = np.asarray(df_s[var_id_no2]) * cfg.units_conversion.sensor['NO2']
                aim_ratio = np.asarray(df_s['NO_NO2_ratio_Legerova']) * cfg.units_conversion.aim['NO2']
                no = no2 * aim_ratio
                nox = no + no2
                conc_id[var][id + 'obs_data'] = nox
                conc_id[var][id + 'obs_datetime'] = [time.to_pydatetime() for time in df_s['time']]
            elif var == 'PM10-2.5':
                var_id_pm10 = cfg.variable_names.sensor['PM10'] + id2
                var_id_pm25 = cfg.variable_names.sensor['PM25'] + id2
                conc_id[var][id + 'obs_data'] = np.asarray(df_s[var_id_pm10]) * cfg.units_conversion.sensor['PM10'] - \
                                                np.asarray(df_s[var_id_pm25]) * cfg.units_conversion.sensor['PM25']
                conc_id[var][id + 'obs_datetime'] = [time.to_pydatetime() for time in df_s['time']]
            elif var in ['PM10all', 'e', 'tke', 'tke_res', 'ws']:
                continue
            else:
                var_id = cfg.variable_names.sensor[var] + id2
                conc_id[var][id+'obs_data'] = np.asarray(df_s[var_id]) * cfg.units_conversion.sensor[var]
                conc_id[var][id+'obs_datetime'] = [time.to_pydatetime() for time in df_s['time']]
        except:
            pass

    return conc_id

def read_station_concentrations_aim(cfg, conc_id, st_id, id, sep=';'):
    """ """
    df = pd.read_csv(cfg.observation_file_aim, sep=sep)
    # filter station
    df_s = df[df['meas_prg_code'] == st_id]
    del df
    df_s['time'] = pd.to_datetime(df_s['date'], format=cfg.datetime_formats.aim).dt.tz_localize(timezone.utc)
    df_s['time'] = pd.to_datetime(df_s['time'], format='%Y-%m-%d %H:%M:%S')
    df_s.index = df_s['time']

    # df_ss = df_s[cfg.date_start:cfg.date_end]
    df_ss = df_s[(df_s.time >= cfg.date_start) &
                 (df_s.time <= cfg.date_end)]

    for var in conc_id.keys():
        if var == 'PM10-2.5':
            data_PM10 = np.asarray(df_ss[cfg.variable_names.aim['PM10']]) * cfg.units_conversion.aim['PM10']
            data_PM25 = np.asarray(df_ss[cfg.variable_names.aim['PM25']]) * cfg.units_conversion.aim['PM25']
            data_PM10[data_PM10 < 0.0] = np.nan
            data_PM25[data_PM25 < 0.0] = np.nan
            data = data_PM10 - data_PM25
            conc_id[var][id + 'obs_data'] = data
            conc_id[var][id + 'obs_datetime'] = [time.to_pydatetime() for time in df_ss['time']]
        elif var in ['PM10all', 'e', 'tke', 'tke_res', 'ws']:
            continue
        else:
            data = np.asarray(df_ss[cfg.variable_names.aim[var]]) * cfg.units_conversion.aim[var]
            data[data < 0.0] = np.nan
            conc_id[var][id+'obs_data'] = data
            conc_id[var][id+'obs_datetime'] = [time.to_pydatetime() for time in df_ss['time']]

    return conc_id

def find_palm_loc(cfg, palm, conc_id, lat, lon, height):
    """ """
    cfg.palm[palm]._settings['skip'] = False
    if not os.path.isfile(cfg.palm[palm].palm_file):
        print('PALM file: {}, does not exists, skip this palm case'.format(cfg.palm[palm].palm_file))
        cfg.palm[palm]._settings['skip'] = True
        return 0, 0, 0, 0

    nc = Dataset(cfg.palm[palm].palm_file, 'r')

    type = cfg.palm[palm].type

    x, y = nc.variables['x'][:] + nc.origin_x, nc.variables['y'][:] + nc.origin_y

    transformer = Transformer.from_crs(CRS.from_user_input(cfg.srid_palm),
                                       CRS.from_user_input(cfg.srid_wgs84))
    X, Y = np.meshgrid(x, y)
    plat, plon = transformer.transform(X, Y)

    i, j = findnearest(plat, plon, (lat, lon))

    # read k
    if type == '3d':
        z = nc.variables['zu_3d'][:]
        try:
            fv = next(iter(conc_id))
            v = nc.variables[conc_id[fv]['palm']][0, :, j, i]
            try:
                last_terr = np.argwhere(v.mask)[-1]
            except:
                last_terr = np.argwhere(v < -9998.0)[-1]
                # first_air = last_terr + 1
        except:
            print('Problem with finding height -> k')
            exit(1)

        k = find_nearest(z-z[last_terr], height)
    elif type == 'mask':
        ku_above_surf = nc.variables['ku_above_surf'][:]
        z = cfg.palm[palm].dz * ku_above_surf - cfg.palm[palm].dz / 2.0
        k = find_nearest(z, height)
        if k == 0:
            k += 1
    else:
        print('Unknown palm output type, exit')
        exit(1)
    nc.close()

    # calculate distance
    # revert obs lat, lon to x, y
    transformer = Transformer.from_crs(CRS.from_user_input(cfg.srid_wgs84),
                                       CRS.from_user_input(cfg.srid_palm))
    x_o, y_o = transformer.transform(lat, lon)
    x_p, y_p = x[i], y[j]

    dist = np.sqrt((x_p - x_o) ** 2 + (y_p - y_o) ** 2)

    return i, j, k, dist

def read_palm(cfg, palm, main_station, conc_id, p_i, p_j, p_k):
    """ """
    if cfg.palm[palm].skip:
        return conc_id

    nc = Dataset(cfg.palm[palm].palm_file, 'r')
    p_times = nc.variables['time'][:]
    if p_times.mask.size == 1:
        p_times_mask = np.ones(p_times.size, dtype=bool)
    else:
        p_times_mask = ~p_times.mask
    p_times = p_times[p_times_mask].data.squeeze()
    # p_times = [datetime.strptime(nc_palm.origin_time, '%Y-%m-%d %H:%M:%S +00').astimezone(pytz.timezone('Europe/Prague')) + timedelta(seconds=nct) for nct in p_times]
    p_times = [datetime.strptime(nc.origin_time, cfg.datetime_formats.palm).astimezone(timezone.utc) + timedelta(seconds=int(nct)) for nct in p_times]
    if cfg.palm_average:
        start_time = p_times[0] - timedelta(seconds=600)
        end_time   = p_times[-1]
        difference = end_time - start_time
        time_diffs = int(difference.total_seconds() / cfg.avg_interval) + 2
        time_grid = [start_time + timedelta(seconds=n * int(cfg.avg_interval)) for n in range(time_diffs)]
        # TODO: Here we take start interval
        time_grid_middle = [start_time + timedelta(seconds=(n) * int(cfg.avg_interval)) for n in range(time_diffs-1)]
        avg_time_mask = []
        for it in range(len(time_grid) - 1):
            avg_temp = []
            for i_temp, o_time in enumerate(p_times):
                if not ((cfg.date_start - timedelta(seconds=3600)) <= o_time and o_time <= (cfg.date_end + timedelta(seconds=3600))):
                    continue
                if time_grid[it] < o_time <= time_grid[it + 1]:
                    avg_temp.append(i_temp)
            avg_time_mask.append(avg_temp)

    # loop over variables
    for var in conc_id.keys():
        # try:
        if var == 'NOx':
            palm_var_NO  = cfg.variable_names.palm['NO']
            palm_var_NO2 = cfg.variable_names.palm['NO2']
            palm_var = nc.variables[palm_var_NO][p_times_mask, p_k, p_j, p_i] * \
                        cfg.units_conversion.palm['NO'] + \
                       nc.variables[palm_var_NO2][p_times_mask, p_k, p_j, p_i] * \
                        cfg.units_conversion.palm['NO2']
            print('\t\t', 'NOx')
        elif var == 'PM10sp':
            palm_var_PM10 = 'kc_PM10'
            palm_var_PM10sp = 'kc_PM10sp'
            palm_var = nc.variables[palm_var_PM10sp][p_times_mask, p_k, p_j, p_i] * \
                       cfg.units_conversion.palm['PM10sp']
            print('\t\t', 'PM10 - PM10sp')

        elif var == 'PM10-2.5':
            palm_var_PM10 = 'kc_PM10'
            palm_var_PM25 = 'kc_PM25'
            palm_var = nc.variables[palm_var_PM10][p_times_mask, p_k, p_j, p_i] * \
                       cfg.units_conversion.palm['PM10'] - \
                       nc.variables[palm_var_PM25][p_times_mask, p_k, p_j, p_i] * \
                       cfg.units_conversion.palm['PM25']
            print('\t\t', 'PM10 - PM2.5')

        elif var == 'PM10all':
            conc_id[var][palm + main_station + '_data'] = np.nan
            conc_id[var][palm + main_station + '_datetime'] = np.nan
        elif var == 'e':
            palm_var_name = 'e'  # conc_id[var]['palm']
            palm_var = nc.variables[palm_var_name][p_times_mask, p_k, p_j, p_i]
            print('\t\t', palm_var_name)

        elif var in ['tke', 'tke_res']:
            palm_var_name = 'tke'
            u = nc.variables['u'][p_times_mask, p_k, p_j, p_i]
            v = nc.variables['v'][p_times_mask, p_k, p_j, p_i]
            w = nc.variables['w'][p_times_mask, p_k, p_j, p_i]
            u_sq = u ** 2
            v_sq = v ** 2
            w_sq = w ** 2
            uu = nc.variables['uu'][p_times_mask, p_k, p_j, p_i]
            vv = nc.variables['vv'][p_times_mask, p_k, p_j, p_i]
            ww = nc.variables['ww'][p_times_mask, p_k, p_j, p_i]
            u_u_ = (uu - u_sq)
            v_v_ = (vv - v_sq)
            w_w_ = (ww - w_sq)
            palm_var = u_u_ / 2.0 + v_v_ / 2.0 + w_w_ / 2.0
            if var == 'tke':
                e = nc.variables['e'][p_times_mask, p_k, p_j, p_i]
                palm_var += e

            print('\t\t', var)

        elif var == 'ws':
            palm_var_name = 'ws'
            u = nc.variables['u'][p_times_mask, p_k, p_j, p_i]
            v = nc.variables['v'][p_times_mask, p_k, p_j, p_i]
            w = nc.variables['w'][p_times_mask, p_k, p_j, p_i]
            u_sq = u ** 2
            v_sq = v ** 2
            w_sq = w ** 2
            palm_var = np.sqrt(u_sq + v_sq + w_sq)
            print('\t\t', palm_var_name)

        else:
            palm_var_name = cfg.variable_names.palm[var]      #conc_id[var]['palm']
            palm_var = nc.variables[palm_var_name][p_times_mask, p_k, p_j, p_i] * cfg.units_conversion.palm[var]
            print('\t\t', palm_var_name)

        # do average and/or save into dict
        if cfg.palm_average:
            palm_avg = np.zeros(len(time_grid) - 1)
            for it in range(len(time_grid) - 1):
                if len(avg_time_mask[it]) == 0:
                    palm_avg[it] = np.nan
                else:
                    try:
                        palm_avg[it] = np.nanmean(palm_var[avg_time_mask[it]], axis=0)
                    except:
                        palm_avg[it] = np.nan

            conc_id[var][palm + main_station + '_data'] = palm_avg
            conc_id[var][palm + main_station + '_datetime'] = time_grid_middle
        else:
            conc_id[var][palm + main_station  + '_data'] = palm_var
            conc_id[var][palm + main_station  + '_datetime'] = p_times

    nc.close()

    return conc_id


def read_cams(cfg, conc_id, lat, lon, id):
    """ """
    nc = Dataset(cfg.cams_file, 'r')

    c_lat, c_lon = nc.variables['latitude'][:], nc.variables['longitude'][:]
    # find nearest point
    j = find_nearest(c_lat, lat)
    i = find_nearest(c_lon, lon)

    transformer = Transformer.from_crs(CRS.from_user_input(cfg.srid_wgs84),
                                       CRS.from_user_input(cfg.srid_palm))
    x_o, y_o = transformer.transform(lat, lon)
    x_c, y_c = transformer.transform(c_lat[j], c_lon[i])

    dist = np.sqrt((x_c - x_o) ** 2 + (y_c - y_o) ** 2)

    # read times
    origin_time = nc.variables['time'].long_name.split(' ')[-1]
    origin_time = datetime.strptime(origin_time, '%Y%m%d').astimezone(timezone.utc)
    tflag = nc.variables['time'][:].data
    c_times = [origin_time + timedelta(hours=float(h)) for h in tflag]

    select_times = []
    c_times_n = []
    for ct, c_time in enumerate(c_times):
        if cfg.date_start <= c_time <= cfg.date_end:
            select_times.append(ct)
            c_times_n.append(c_time)

    if len(c_times) == 0:
        return conc_id

    # read variables
    for var in conc_id.keys():
        try:
            if var == 'NOx':
                no_var = cfg.variable_names.cams['NO']
                no2_var = cfg.variable_names.cams['NO2']
                conc_id[var]['cams_data'] = nc.variables[no_var][select_times, cfg.cams_level, j, i] * cfg.units_conversion.cams['NO'] + \
                                            nc.variables[no2_var][select_times, cfg.cams_level, j, i] * cfg.units_conversion.cams['NO2']
                conc_id[var]['cams_datetime'] = c_times_n
            elif var == 'PM10-2.5':
                pm10_var = cfg.variable_names.cams['PM10']
                pm25_var = cfg.variable_names.cams['PM25']
                conc_id[var]['cams_data'] = nc.variables[pm10_var][select_times, cfg.cams_level, j, i] * \
                                            cfg.units_conversion.cams['PM10'] + \
                                            nc.variables[pm25_var][select_times, cfg.cams_level, j, i] * \
                                            cfg.units_conversion.cams['PM25']
                conc_id[var]['cams_datetime'] = c_times_n
            else:
                cams_var = cfg.variable_names.cams[var]
                conc_id[var]['cams_data'] = nc.variables[cams_var][select_times, cfg.cams_level, j, i] * cfg.units_conversion.cams[var]
                conc_id[var]['cams_datetime'] = c_times_n
        except:
            pass

    return conc_id

def calculate_sunrise_sunset(cfg):
    """ Function that will based on configuration latitude and longitude and datetime calculate time of sunrise and sunsite.
        Further used in plotting to show daytime and nighttime (morning, evening)
    """
    sun = Sun(cfg.latitude, cfg.longitude)
    delta = cfg.date_end - cfg.date_start

    sunrise = []
    sunset = []
    sunset.append(cfg.date_start)
    for i in range(delta.days + 1):
        sunrise.append(sun.get_sunrise_time(cfg.date_start + timedelta(days=i)))
        sunset.append(sun.get_sunset_time(cfg.date_start + timedelta(days=i)))
    sunrise.append(cfg.date_end)

    return sunrise, sunset

def nearest(items, pivot):
    min_val = min(items, key=lambda x: abs(x - pivot))
    min_idx = items.index(min_val)
    return min_idx, min_val

def merge_times(cfg, conc_id, iobs):
    """ Merge times between PALM and observation, save to dataframe, do statistics and print to csv, plot scatter """
    for var in conc_id.keys():
        if var in ['PM10all', 'e', 'tke', 'tke_res', 'ws']:
            continue
        first = True
        for main_station in cfg.obs_loop[iobs].main_obs:
            if not first:
                if main_station in dfs['station']:
                    continue
            palm_conc_dict = {}
            id = cfg.observation[main_station].id
            # id = main_station
            station_datetime = conc_id[var][id+'obs_datetime']
            station_conc     = conc_id[var][id+'obs_data']
            palm_conc_dict['datetime'] = station_datetime
            palm_conc_dict['obs_val'] = station_conc

            for palm in cfg.palm._settings.keys():
                palm_name = cfg.palm[palm].case_name
                if cfg.palm[palm].skip:
                    continue
                if not palm + main_station + '_datetime' in conc_id[var].keys():
                    continue
                palm_conc_dict[palm_name] = []
                palm_datetime = conc_id[var][palm + main_station + '_datetime']
                palm_conc     = conc_id[var][palm + main_station + '_data']

                # find nearest time from PALM
                for st_id, station_time in enumerate(station_datetime):
                    station_time = station_time.astimezone(timezone.utc)
                    p_idx, _ = nearest(palm_datetime, station_time)
                    act_dif = (station_time - palm_datetime[p_idx]).total_seconds()
                    if abs(act_dif) > 3600.0 or np.isnan(station_conc[st_id]):
                        palm_conc_dict[palm_name].append(np.nan)
                        continue
                    palm_conc_dict[palm_name].append(palm_conc[p_idx])

            # create dataframe
            df = pd.DataFrame(palm_conc_dict).assign(station=main_station)
            csv_name = os.path.join(cfg.plotting.path_csv, main_station + '_' + var + '.csv')
            df.to_csv(csv_name)
            if first:
                dfs = df
                first = False
            else:
                dfs = pd.concat([dfs, df])

        # csv_name = os.path.join(cfg.plotting.path_csv, 'all_stations_' + var + '.csv')
        # dfs.to_csv(csv_name)

def merge_csv(cfg):
    """ Merge all csv into single one """
    for var in cfg.variables:
        if var in ['PM10all', 'e', 'tke', 'tke_res', 'ws']:
            continue
        mask = os.path.join(cfg.plotting.path_csv, '*' + '_' + var + '.csv')
        stations = glob.glob(mask)
        pds = []
        for station in stations:
            pds.append(pd.read_csv(station))

        dfs = pd.concat(pds)
        csv_name = os.path.join(cfg.plotting.path_csv, 'all_stations_' + var + '.csv')
        dfs.to_csv(csv_name)