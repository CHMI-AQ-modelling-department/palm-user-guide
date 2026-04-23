import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import seaborn as sns
matplotlib.use('TkAgg')
from .utils import calculate_sunrise_sunset, get_time_grid_ticks
import os
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from matplotlib.dates import HourLocator, MonthLocator, YearLocator
import matplotlib.dates as mdates
import matplotlib.dates as plt_dates

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rcParams['xtick.major.pad']='8'
plt.rc('font', size=12)


def plotting(cfg, iobs, station_name, station_id, conc_id):
    """ """
    if not cfg.plotting.show_plots:
        plt.ioff()

    if cfg.plotting.sunrise_sunset:
        sunrise, sunset = calculate_sunrise_sunset(cfg)

    for var in conc_id.keys():
        print('Plotting var:', var)

        fig, ax = plt.subplots(figsize=(20, 12))

        ax.xaxis.set_minor_locator(plt_dates.HourLocator(byhour=range(0, 24, int(cfg.plotting.hourlocator))))
        ax.xaxis.set_minor_formatter(plt_dates.DateFormatter('%-H'))
        ax.xaxis.set_major_locator(plt_dates.DayLocator())
        ax.xaxis.set_major_formatter(plt_dates.DateFormatter('%-d.%-m.'))
        # xticks = ax.get_xticks().tolist()
        # labels = ['\n' + item.get_text() for item in ax.get_xticklabels()]
        # ax.set_xticks(xticks)
        # ax.set_xticklabels(labels)
        ax.set_xlabel(r'Time (UTC)', fontsize=22)
        # plt.xlim(cfg.date_start, cfg.date_end)

        plt.ylabel(r"{}".format(cfg.plotting.var_labels[var]), fontsize=22)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

        # plt.grid(True)
        # plt.minorticks_on()
        plt.grid(which='major', linewidth='1', color='black')
        plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        # ax.xaxis.set_minor_locator(HourLocator(byhour=None, interval=6, tz=None))
        # ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H"))
        # ax.xaxis.set_major_locator(HourLocator(byhour=None, interval=24, tz=None))
        # ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%d. %H"))
        # plt.xticks(rotation=45)

        # time_ticks, time_ticks_loc = get_time_grid_ticks(cfg)
        # ax.set_xticks(ticks)
        # ax.set_xticklabels(ticks.strftime('%H:%M'));

        # observation
        for station, ls, cl in zip(cfg.obs_loop[iobs].adjacent_obs, cfg.obs_loop[iobs].palm_ls, cfg.obs_loop[iobs].palm_cl):
            if var in ['PM10all', 'e', 'tke', 'tke_res', 'ws']:
                continue
            id = cfg.observation[station].id
            # passive
            if id+'passive_data' in conc_id[var].keys():
                plt.axhline(y=conc_id[var][id+'passive_data'], lw=3, ls=ls, color=cl, label='Passive ' + cfg.observation[station].case_name)
                # marker='x', markersize=16,
            else:
                try:
                    plt.plot(conc_id[var][id+'obs_datetime'], conc_id[var][id+'obs_data'], lw=3, ls=ls, color=cl, label='Observation ' + cfg.observation[station].case_name)
                    # marker='x', markersize=16,
                except:
                    pass

        # PALMS
        palm_here = False
        if 'palm' in cfg._settings.keys():
            for main_station, palm_ls, palm_cl in zip(cfg.obs_loop[iobs].main_obs, cfg.obs_loop[iobs].palm_ls, cfg.obs_loop[iobs].palm_cl):
                for palm in cfg.palm._settings.keys():
                    if cfg.palm[palm].skip:
                        continue
                    if not palm + main_station + '_datetime' in conc_id[var].keys():
                        continue
                    palm_here = True
                    if var == 'PM10b':
                        # include also PM10
                        plt.plot(conc_id['PM10'][palm + main_station + '_datetime'],
                                 conc_id['PM10'][palm + main_station + '_data'], lw=3,
                                 ls=cfg.palm[palm].ls, color=cfg.palm[palm].color,
                                 label='PALM PM10: {} in {}'.format(cfg.palm[palm].case_name, cfg.observation[main_station].case_name)
                                      if len(cfg.obs_loop[iobs].main_obs) > 1 else 'PALM PM10: {}'.format(cfg.palm[palm].case_name))
                        plt.plot(conc_id[var][palm + main_station + '_datetime'],
                                 conc_id[var][palm + main_station + '_data'], lw=3,
                                 ls=cfg.palm[palm].ls, color=cfg.palm[palm].color,
                                 label='PALM PM10b: {} in {}'.format(cfg.palm[palm].case_name, cfg.observation[main_station].case_name)
                                      if len(cfg.obs_loop[iobs].main_obs) > 1 else 'PALM PM10b: {}'.format(cfg.palm[palm].case_name))
                    elif var == 'PM10all':
                        try:
                            pm10b = conc_id['PM10b'][palm + main_station + '_data']
                            pm10sp = conc_id['PM10sp'][palm + main_station + '_data']
                            pm10 = conc_id['PM10'][palm + main_station + '_data']

                            pm10_stack = {
                                'PM10b': pm10b,
                                'PM10sp': pm10sp,
                                'PM10 other': pm10 - pm10b - pm10sp
                            }
                            plt.stackplot(conc_id['PM10'][palm + main_station + '_datetime'],
                                         pm10_stack.values(),
                                         labels=pm10_stack.keys(), alpha=0.8, zorder=3)
                        except:
                            pass
                    else:
                        plt.plot(conc_id[var][palm + main_station + '_datetime'],
                                 conc_id[var][palm + main_station + '_data'], lw=3,
                                 ls=cfg.palm[palm].ls, color=cfg.palm[palm].color, #palm_cl, #
                                 label='PALM: {} in {}'.format(cfg.palm[palm].case_name, cfg.observation[main_station].case_name)
                                      if len(cfg.obs_loop[iobs].main_obs) > 1 else 'PALM: {}'.format(cfg.palm[palm].case_name))


        if 'cams_datetime' in conc_id[var].keys(): # and not var == 'PM10all':
            plt.plot(conc_id[var]['cams_datetime'], conc_id[var]['cams_data'], lw=3, ls=':', color='orange', label='CAMS')

        # Plot daytime / nighttime using sunrise and sunset
        if cfg.plotting.sunrise_sunset:
            for suns, sunr in zip(sunset, sunrise):
                plt.axvspan(suns, sunr, color='lightgrey', alpha=0.75, zorder=1)

        plt.xlim(cfg.date_start, cfg.date_end)
        plt.ylim(bottom=0.0)
        plt.legend(loc='best', fontsize=16, ncol=cfg.plotting.leg_cols)
        plt.subplots_adjust(bottom=0.2, right=0.75)

        if len(plt.gca().lines) > 1 or palm_here:
            plt.savefig(os.path.join(cfg.plotting.path, 'station_{}_{}.png'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path, 'station_{}_{}.svg'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path, 'station_{}_{}.pdf'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path, 'station_{}_{}.eps'.format(station_id, var)))

        # Plot semilogy plot
        try:
            if not var in ['PM10all', 'e']:
                plt.yscale('log')
                if len(plt.gca().lines) > 1 or palm_here:
                    plt.savefig(os.path.join(cfg.plotting.path_semilogy, 'station_{}_{}.png'.format(station_id, var)))
                    plt.savefig(os.path.join(cfg.plotting.path_semilogy, 'station_{}_{}.svg'.format(station_id, var)))
                    plt.savefig(os.path.join(cfg.plotting.path_semilogy, 'station_{}_{}.pdf'.format(station_id, var)))
                    plt.savefig(os.path.join(cfg.plotting.path_semilogy, 'station_{}_{}.eps'.format(station_id, var)))
        except:
            pass

        plt.yscale('linear')
        # fig.set_figheight(7)
        # fig.set_figwidth(14)
        # plt.gca().set_aspect(2)
        plt.ylim([0.0, cfg.plotting.ylims[var]])
        fig.set_size_inches(16.0, 5.0)
        if len(plt.gca().lines) > 1 or palm_here:
            plt.savefig(os.path.join(cfg.plotting.path_smaller, 'station_{}_{}.png'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path_smaller, 'station_{}_{}.svg'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path_smaller, 'station_{}_{}.pdf'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path_smaller, 'station_{}_{}.eps'.format(station_id, var)))

        fig.set_size_inches(14, 10)
        plt.ylim([0.0, cfg.plotting.ylims[var]])
        if len(plt.gca().lines) > 1 or palm_here:
            plt.savefig(os.path.join(cfg.plotting.path_fixed, 'station_{}_{}.png'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path_fixed, 'station_{}_{}.svg'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path_fixed, 'station_{}_{}.pdf'.format(station_id, var)))
            plt.savefig(os.path.join(cfg.plotting.path_fixed, 'station_{}_{}.eps'.format(station_id, var)))


        if not cfg.plotting.show_plots:
            plt.close('all')

def scatter_from_stations(cfg):
    # Scatter plot
    for var in cfg.variables:
        if var in ['PM10all', 'e', 'tke', 'tke_res', 'ws', 'PM10b', 'PM10sp']:
            continue
        # var = 'PM10'
        dfs = pd.read_csv(os.path.join(cfg.plotting.path_csv, 'all_stations_' + var + '.csv'))
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')
        plt.figure(figsize=(14, 10))
        plt.subplot(1, 1, 1)
        # plt.title('Palm vs Observarion, var {}'.format(var), fontsize=30)
        plt.xlabel('Observation / -', fontsize=30)
        plt.ylabel('PALM', fontsize=30)
        min_v, max_v = dfs['obs_val'].min(), dfs['obs_val'].max()
        for palm in cfg.palm._settings.keys():
            try:
                palm_name = cfg.palm[palm].case_name
                sns.scatterplot(data=dfs, x='obs_val', y=palm_name, hue='station')
                min_v = min([min_v, dfs[palm_name].min()])
                max_v = min([max_v, dfs[palm_name].max()])
            except:
                pass
        plt.plot([min_v, max_v], [min_v, max_v], lw=3, color='red')
        plt.xlim([min_v, max_v])
        plt.ylim([min_v, max_v])
        plt.savefig(os.path.join(cfg.plotting.path_csv, 'scatter_{}.png'.format(var)))
        plt.savefig(os.path.join(cfg.plotting.path_csv, 'scatter_{}.png'.format(var)))
        plt.savefig(os.path.join(cfg.plotting.path_csv, 'scatter_{}.png'.format(var)))
        plt.savefig(os.path.join(cfg.plotting.path_csv, 'scatter_{}.png'.format(var)))
        #plt.show()
        if not cfg.plotting.show_plots:
            plt.close('all')