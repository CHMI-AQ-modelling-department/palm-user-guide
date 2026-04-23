import numpy
from datetime import datetime

import numpy as np

""" Copied values from passive sensor from aq """

# datetime and value
# monthly averages
# stations ordered, with lat, lon coordinates
pass_dates = ['2022-02-01 00:00:00', '2022-03-01 00:00:00', '2022-04-01 00:00:00', '2022-05-01 00:00:00', '2022-06-01 00:00:00', '2022-07-01 00:00:00', '2022-08-01 00:00:00', '2022-09-01 00:00:00', '2022-10-01 00:00:00', '2022-11-01 00:00:00', '2022-12-01 00:00:00', '2023-01-01 00:00:00']

pass_datetimes = [datetime.strptime(pass_date, '%Y-%m-%d %H:%M:%S') for pass_date in pass_dates]

ps = {}

ps['pass_samp1'] = {}
ps['pass_samp1']['datetime'] = pass_datetimes
ps['pass_samp1']['data'] = np.asarray([52.7, 66.1, 60, 62.3, 60.2, 53, 57.8, 58.6, 50.3, 48.1, 53, 53.5])

ps['pass_samp2'] = {}
ps['pass_samp2']['datetime'] = pass_datetimes
ps['pass_samp2']['data'] = np.asarray([31.7, np.nan, 52.6, 57.5, 65.4, 59.2, 61.9, 56.4, 56.1, 50.9, 47.2, 51.3])

ps['pass_samp3'] = {}
ps['pass_samp3']['datetime'] = pass_datetimes
ps['pass_samp3']['data'] = np.asarray([45.5, 54.1, 47.9, 59.3, 57.3, 51.1, 54.4, 52.8, 43.9, 43.6, 43.6, np.nan])

ps['pass_samp4'] = {}
ps['pass_samp4']['datetime'] = pass_datetimes
ps['pass_samp4']['data'] = np.asarray([37.5, 53.9, 50.3, 54, 60.4, 46, 61.6, 52.1, 45.6, 39.9, 43.5, 42.1])

ps['pass_samp5'] = {}
ps['pass_samp5']['datetime'] = pass_datetimes
ps['pass_samp5']['data'] = np.asarray([40.7, 50, 45.4, 48.7, 47.7, 43.3, 51.6, 50.3, 47.7, 45.5, 45.4, 46.3])

ps['pass_samp6'] = {}
ps['pass_samp6']['datetime'] = pass_datetimes
ps['pass_samp6']['data'] = np.asarray([42.3, 51.4, 50.4, 47.3, 46.4, 37.5, 49.9, 50.3, 45.9, 40.1, 43.6, 45.2])

ps['pass_samp7'] = {}
ps['pass_samp7']['datetime'] = pass_datetimes
ps['pass_samp7']['data'] = np.asarray([37.3, 54.8, 49, 47.5, 43.9, 46, 46.5, 43.4, 41.2, 37.4, 37.9, 40.9])

ps['pass_samp8'] = {}
ps['pass_samp8']['datetime'] = pass_datetimes
ps['pass_samp8']['data'] = np.asarray([44.6, 48.6, 43.8, 39.2, 41.1, 36.9, 47.6, 46.9, 46.4, 45, 42.3, 37.4])

ps['pass_samp9'] = {}
ps['pass_samp9']['datetime'] = pass_datetimes
ps['pass_samp9']['data'] = np.asarray([39.3, 51.7, 46.6, 46.1, 46.3, 43.1, 47.3, 45.8, 44.1, 36.5, 36.7, 34.4])

ps['pass_samp10'] = {}
ps['pass_samp10']['datetime'] = pass_datetimes
ps['pass_samp10']['data'] = np.asarray([40, 48.3, 41.8, 45.2, 45.7, 37.2, 39.7, 39.7, 36.6, 40.6, 46.2, 40.2])

ps['pass_samp11'] = {}
ps['pass_samp11']['datetime'] = pass_datetimes
ps['pass_samp11']['data'] = np.asarray([29.4, 55.4, 38.4, 44.1, 40.3, 42.4, 50.5, 46.1, 44.3, 37.9, 36.8, 31.7])

ps['pass_samp12'] = {}
ps['pass_samp12']['datetime'] = pass_datetimes
ps['pass_samp12']['data'] = np.asarray([39.9, 45, 43.3, 41.5, 42.1, 38.9, 45.2, 46.4, 40.6, 38.3, 39.7, 35.7])

ps['pass_samp13'] = {}
ps['pass_samp13']['datetime'] = pass_datetimes
ps['pass_samp13']['data'] = np.asarray([35.5, 42.3, 40, 46.4, 44.3, 44.8, np.nan, 43.5, 37.1, 37.1, 38.9, 37.3])

ps['pass_samp14'] = {}
ps['pass_samp14']['datetime'] = pass_datetimes
ps['pass_samp14']['data'] = np.asarray([39.3, 45.8, 41.8, 47, 41.9, 43.6, 43, 42.2, 36, 33.8, 35.5, 32.5])

ps['pass_samp15'] = {}
ps['pass_samp15']['datetime'] = pass_datetimes
ps['pass_samp15']['data'] = np.asarray([33.5, 41.6, 38.2, 40.2, 43.3, 34.8, np.nan, 35.7, 36.1, 35, 36.7, 32.5])

ps['pass_samp16'] = {}
ps['pass_samp16']['datetime'] = pass_datetimes
ps['pass_samp16']['data'] = np.asarray([32.6, 40.7, 35, 38.2, np.nan, 32.9, 40.9, 37.7, 33.5, 38.8, 34.4, 28.2])

ps['pass_samp17'] = {}
ps['pass_samp17']['datetime'] = pass_datetimes
ps['pass_samp17']['data'] = np.asarray([32, 43.4, 37.7, 38.3, 36.3, 33.5, 33.5, 31, 30.8, 30.8, 33.3, 27.9])

ps['pass_samp18'] = {}
ps['pass_samp18']['datetime'] = pass_datetimes
ps['pass_samp18']['data'] = np.asarray([34.9, 42.8, 34, 31.2, 29.8, 30.1, 33.2, 31.3, 30, 29.5, 33, 26.2])

ps['pass_samp19'] = {}
ps['pass_samp19']['datetime'] = pass_datetimes
ps['pass_samp19']['data'] = np.asarray([34.5, 39.2, 25.5, 29.2, 27.9, 26.4, 31.4, 32.6, 30.1, 32.8, 33.9, 29.8])

ps['pass_samp20'] = {}
ps['pass_samp20']['datetime'] = pass_datetimes
ps['pass_samp20']['data'] = np.asarray([32.3, 35.8, 30.4, np.nan, 25.7, 27.1, 29.8, 30.1, 32.9, 28.4, 33.3, 32.2])

def read_station_concentrations_passive(cfg, st_id):
    """ """
    # load correct station
    try:
        dates = ps[st_id]['datetime']
        datas = ps[st_id]['data']
    except:
        print('Bad station in passive, exit')
        exit(1)

    # select correct time
    for idx, date in enumerate(dates):
        if date.year == cfg.date_start.year and date.month == cfg.date_start.month:
            return datas[idx]

    return np.nan