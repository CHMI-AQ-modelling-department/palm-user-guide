from utils.config import load_config, cfg
from utils.utils import *
from utils.plotting import plotting, scatter_from_stations
from utils.passive import read_station_concentrations_passive
from argparse import ArgumentParser

argp = ArgumentParser(description=__doc__)
argp.add_argument('-c', '--config', help='configuration file')
argp.add_argument('--extend', action='store_true', help='extend or replace obs_loop from default_config.yaml')
argp.add_argument('--no-extend', dest='extend', action='store_false', help='extend or replace obs_loop from default_config.yaml')
argp.set_defaults(extend=True)

verbosity = argp.add_mutually_exclusive_group()
verbosity.add_argument('-v', '--verbose', action='store_const',
        dest='verbosity_arg', const=2, help='increase verbosity')
verbosity.add_argument('-s', '--silent', action='store_const',
        dest='verbosity_arg', const=0, help='print only errors')

# load config file
argv = argp.parse_args()
load_config(argv)

for iobs in cfg.obs_loop._settings.keys():
    print('Processing iobs')
    conc_id = {}
    for var in cfg.variables:
        conc_id[var] = {}

    # Load main observation station
    for main_station in cfg.obs_loop[iobs].main_obs:
        # main_station = cfg.obs_loop[iobs].main_obs
        print('\tMain Station: {}'.format(main_station))
        # Read station location
        lat, lon, height = read_station_loc(cfg, cfg.observation[main_station].id)

        # Loop over PALM for each station
        if 'palm' in cfg._settings.keys():
            for palm in cfg.palm._settings.keys():
                if cfg.palm[palm].palm_file == '':
                    cfg.palm[palm]._settings['skip'] = True
                    continue
                p_i, p_j, p_k, dist = find_palm_loc(cfg, palm, conc_id, lat, lon, height)
                print('\t', palm, p_i, p_j, dist, p_k, height)

                if dist > cfg.dist:
                    continue

                # Read palm output variable
                conc_id = read_palm(cfg, palm, main_station, conc_id, p_i, p_j, p_k)

    for main_station in cfg.obs_loop[iobs].main_obs:
        if not main_station in cfg.obs_loop[iobs].adjacent_obs:
            cfg.obs_loop[iobs]._settings['adjacent_obs'] = cfg.obs_loop[iobs].adjacent_obs + [main_station]

    for station in cfg.obs_loop[iobs].adjacent_obs:
        print('\tProcessing Station: {}'.format(station))
        # Read all the data from station
        if cfg.observation[station].type == 'sensor':
            conc_id = read_station_concentrations(cfg, conc_id, cfg.observation[station].id2, cfg.observation[station].id)
        elif cfg.observation[station].type == 'aim':
            conc_id = read_station_concentrations_aim(cfg, conc_id, cfg.observation[station].id, cfg.observation[station].id)
        elif cfg.observation[station].type == 'pass_samp' and 'NO2' in cfg.variables:
            conc_id['NO2'][cfg.observation[station].id+'passive_data'] = read_station_concentrations_passive(cfg, cfg.observation[station].id)


    # read CAMS if available
    if cfg.cams_file != '':
        print('\tProcessing CAMS: {}'.format(cfg.cams_file))
        conc_id = read_cams(cfg, conc_id, lat, lon, cfg.observation[main_station].id)

    # plot it all
    plotting(cfg, iobs, cfg.observation[main_station].case_name, iobs, conc_id)

    # Join all times between observation and PALM -> to dataframe -> statistics -> .csv
    merge_times(cfg, conc_id, iobs)

merge_csv(cfg)

scatter_from_stations(cfg)