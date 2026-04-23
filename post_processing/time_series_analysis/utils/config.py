import os
import sys
import yaml
import datetime
from collections import defaultdict
from datetime import datetime, timedelta, timezone
# from .logging import die, warn, log, verbose

error_output = sys.stderr.write

def die(s, *args, **kwargs):
    """Write message to error output and exit with status 1."""

    if args or kwargs:
        error_output(s.format(*args, **kwargs) + '\n')
    else:
        error_output(s + '\n')
    sys.exit(1)

def warn(s, *args, **kwargs):
    """Write message to error output."""

    if args or kwargs:
        error_output(s.format(*args, **kwargs) + '\n')
    else:
        error_output(s + '\n')


class ConfigError(Exception):
    def __init__(self, desc, section=None, key=None):
        self.desc = desc
        self.section = section
        self.key = key

        # Build message
        s = ['Configuration error: ', desc]
        if section:
            s.extend([', item: ', ':'.join(section._get_path()+[key])])
            try:
                v = section._settings[key]
            except KeyError:
                s.append(', missing value')
            else:
                s.extend([', value=', str(v)])
        s.append('.')
        self.msg = ''.join(s)

    def __str__(self):
        return self.msg

class ConfigObj(object):
    """A recursive object within a hierarchical configuration, representing
    a (sub)section as a dictionary from the YAML configuration file. Child
    nodes may be accessed both by the dot notation (section.setting) and the
    item notation (section['setting']).
    """
    # We use __slots__ because we intend to hardly limit (and control) instance
    # members, so that we do not break many potential names of actual settings
    # that are accessed using the dot notation. For the same reason, member and
    # method names (mostly used internally anyway) start with an underscore.
    __slots__ = ['_parent', '_name', '_settings']

    def __init__(self, parent=None, name=None):
        self._parent = parent
        self._name = name
        self._settings = {}

    def __getattr__(self, name):
        try:
            return self._settings[name]
        except KeyError:
            raise AttributeError('Attribute {} not found. Possibly a missing '
                    'configuration setting in section {}.'.format(name,
                        ':'.join(self._get_path())))

    def __getitem__(self, key):
        try:
            return self._settings[key]
        except KeyError:
            raise KeyError('Key {} not found. Possibly a missing configuration '
                    'setting in section {}.'.format(key,
                        ':'.join(self._get_path())))

    def __iter__(self):
        return iter(self._settings.items())

    def _ingest_dict(self, d, overwrite=True, extend=True, check_exist=False):
        for k, v in d.items():
            if isinstance(v, ConfigObj):
                # we are actually ingesting a subtree - replace by its dict
                v = v._settings

            if isinstance(v, dict):
                # For a dictionary (top-level or with only dictionaries above,
                # i.e. a subsection), we recurse
                try:
                    vl = self._settings[k]
                except KeyError:
                    # not yet present: create a new empty child node
                    vl = ConfigObj(self, k)
                    self._settings[k] = vl
                try:
                    vl._ingest_dict(v, overwrite, extend, check_exist)
                except AttributeError:
                    raise ConfigError('Trying to replace a non-dictionary '
                            'setting with a dictionary', self, k)
            elif extend and isinstance(v, list):
                # We extend lists if requested
                vl = self._settings.setdefault(k, [])
                try:
                    vl.extend(v)
                except AttributeError:
                    raise ConfigError('Trying to extend a non-list setting with '
                            'a list', self, k)
            elif v is None and isinstance(self._settings.get(k), ConfigObj):
                # This is a special case: we are replacing an existing section
                # with None. That most probably means that the user has
                # presented an empty section (possibly with all values
                # commented out). In that case, we do not want to erase that
                # section. To actually erase a whole section, the user can
                # still present empty dictionary using the following syntax:
                # section_name: {}
                pass
            else:
                # Non-extended lists and all other objects are considered as
                # values and they are copied as-is (including their subtrees if
                # present). Non-null values are overwritten only if
                # overwrite=True.
                if overwrite:
                    # if check_exist and k not in self._settings:
                        # warn('WARNING: ignoring an unknown setting {}={}.',
                        #         ':'.join(self._get_path()+[k]), v)
                    self._settings[k] = v
                else:
                    if self._settings.get(k, None) is None:
                        self._settings[k] = v

    def _get_path(self):
        if self._parent is None:
            return []
        path = self._parent._get_path()
        path.append(self._name)
        return path


duration_units = {
        'd': 'days',
        'h': 'hours',
        'm': 'minutes',
        's': 'seconds',
        }

def parse_duration(section, item):
    def err():
        raise ConfigError('Bad specification of duration. The correct format is '
                '{num} {unit} [{num} {unit} ...], where {unit} is one of d, h, '
                'm, s. Example: "1 m 3.2 s".', section, item)

    try:
        s = section[item]
    except KeyError:
        err()

    words = s.split()
    n = len(words)
    if n % 2:
        err()

    d = defaultdict(int)
    for i in range(0, n, 2):
        ns, unit = words[i:i+2]
        try:
            num = int(ns)
        except ValueError:
            try:
                num = float(ns)
            except ValueError:
                err()
        try:
            u = duration_units[unit]
        except KeyError:
            err()
        d[u] += num

    return datetime.timedelta(**d)


def load_config(argv):
    """Loads all configuration.

    Configuration is loaded in this order:
    1) initial configuration values
    2) configfile
    3) command-line options
    Each step may overwrite values from previous steps.
    """
    global cfg

    # load default configuration
    cfg_default_path = 'default_config.yaml'  #os.path.join(os.path())
    with open(cfg_default_path, 'r') as f:
        cfg._ingest_dict(yaml.load(f))

    if not argv.extend:
        cfg.obs_loop._settings = {}

    # load settings from user configfile (if available)
    if argv.config:
        with open(argv.config, 'r') as config_file:
            cfg._ingest_dict(yaml.load(config_file), extend=argv.extend, check_exist=True)

    # # Basic verification
    # if not cfg.case:
    #     raise ConfigError('Case name must be specified', cfg, 'case')

    if 'PM10b' in cfg.variables and not 'PM10' in cfg.variables:
        print('Adding PM10 into variables')
        cfg._settings['variables'].append('PM10')

    if 'PM10all' in cfg.variables and not 'PM10' in cfg.variables:
        print('Adding PM10 into variables')
        cfg._settings['variables'].append('PM10')

    if 'PM10all' in cfg.variables and not 'PM10b' in cfg.variables:
        print('Adding PM10b into variables')
        cfg._settings['variables'].append('PM10b')

    if 'PM10all' in cfg.variables and not 'PM10sp' in cfg.variables:
        print('Adding PM10sp into variables')
        cfg._settings['variables'].append('PM10sp')

    # verify all paths
    if not os.path.isdir(cfg.plotting.path):
        # create plot_path
        print('Creating folder: {}'.format(cfg.plotting.path))
        os.mkdir(cfg.plotting.path)

    cfg.plotting._settings['path_fixed'] = os.path.join(cfg.plotting.path, 'fixed_axis')
    if not os.path.isdir(cfg.plotting.path_fixed):
        # create plot_path
        print('Creating folder: {}'.format(cfg.plotting.path_fixed))
        os.mkdir(cfg.plotting.path_fixed)

    cfg.plotting._settings['path_semilogy'] = os.path.join(cfg.plotting.path, 'semilogy')
    if not os.path.isdir(cfg.plotting.path_semilogy):
        # create plot_path
        print('Creating folder: {}'.format(cfg.plotting.path_semilogy))
        os.mkdir(cfg.plotting.path_semilogy)

    cfg.plotting._settings['path_csv'] = os.path.join(cfg.plotting.path, 'csv')
    if not os.path.isdir(cfg.plotting.path_csv):
        # create plot_path
        print('Creating folder: {}'.format(cfg.plotting.path_csv))
        os.mkdir(cfg.plotting.path_csv)

    cfg.plotting._settings['path_smaller'] = os.path.join(cfg.plotting.path, 'smaler')
    if not os.path.isdir(cfg.plotting.path_smaller):
        # create plot_path
        print('Creating folder: {}'.format(cfg.plotting.path_smaller))
        os.mkdir(cfg.plotting.path_smaller)

    for obs in cfg.obs_loop._settings.keys():
        if not 'palm_ls' in cfg.obs_loop[obs]._settings.keys():
           cfg.obs_loop[obs]._settings['palm_ls'] = [ '--', '--', '--', '--', '--']
        if not 'palm_cl' in cfg.obs_loop[obs]._settings.keys():
           # cfg.obs_loop[obs]._settings['palm_cl'] = [ 'red', 'blue', 'green', 'yellow', 'cyan']
           cfg.obs_loop[obs]._settings['palm_cl'] = ['black', 'black', 'black', 'black', 'black']

    cfg._settings['date_start'] = cfg.date_start.astimezone(timezone.utc)
    cfg._settings['date_end']   = cfg.date_end.astimezone(timezone.utc)

cfg = ConfigObj()