import glob
import os
import sys
import getopt

# default list of files
path = ''
mask = '*cpu.*'
n_nodes = 1
configname = ''

# read configuration from command line
# line and parse it
def print_help():
    print('read_cpu_time.py -c <config name>')

# def nearest(items, pivot):
#     return min(items, key=lambda x: abs(x - pivot))

try:
    opts, args = getopt.getopt(sys.argv[1:],"hc:)",["help=","="])
    #print(opts)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif opt in ("-c", "--config"):
            configname = arg

except getopt.GetoptError as err:
    print("Error:", err)
    print_help()
    #sys.exit(2)
# parse options

# get path of the config file
# real run - we need connect current path with relative path to script
runpath = os.path.dirname(os.path.abspath(os.path.join(os.path.abspath(os.path.curdir),sys.argv[0])))

if configname == '':
    # palm_jointoutputs requires domain and resolution
    print("read_cpu_time.py requires <config name>")
    print_help()
    exit(2)


# check supplied params of run
configfile = os.path.join(runpath, configname+'.conf')
if not os.path.isfile(configfile):
    print("Config file "+configfile+" does not exists!")
    print_help()
    exit(2)

# read domain configuration
exec(open(configfile).read())

print('Config file: ', configfile)
print('path:', path)
print('mask: ', mask)
print('n_nodes: ', n_nodes)

files = glob.glob(os.path.join(path, mask))
files.sort()

cpu_time = []
sum_cpu_time = 0.0

for file in files:
    with open(file, 'r') as cpu_file:
        cpu_file.seek(0)
        for line in cpu_file:
            if 'total' in line.split():
                time = float(line.split()[1]) / 3600.0
                sum_cpu_time += time
                cpu_time.append([file.split('/')[-1], time])
                print('Restart: {}, consumed: {:.1f} node hours. {:.1f} real hours'.format(file.split('/')[-1], time * n_nodes, time))

print("Whole run consumed {:.1f} node hours and took {:.1f} real hours. It is Hynek's fault".format(sum_cpu_time * n_nodes, sum_cpu_time))