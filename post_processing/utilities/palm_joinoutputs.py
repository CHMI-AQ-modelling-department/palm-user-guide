import sys
import getopt
import os
import os.path
from shutil import copyfile
import glob
from datetime import datetime
from time import gmtime, strftime
from netCDF4 import Dataset
from math import floor
import numpy as np

# set defaults of parameters
origpath = ''
finalpath = ''
filelist = ['DATA_2D_XY_AV_NETCDF_N02','DATA_3D_AV_NETCDF_N02','DATA_MASK_AV_NETCDF_N02_M01', \
            'SURFACE_DATA_AV_NETCDF_N02', 'DATA_2D_XY_NETCDF_N02', \
            'DATA_3D_NETCDF_N02','DATA_MASK_NETCDF_N02_M01','SURFACE_DATA_NETCDF_N02', \
            'DATA_2D_XY_AV_NETCDF','DATA_3D_AV_NETCDF','DATA_MASK_AV_NETCDF_M01', \
            'SURFACE_DATA_AV_NETCDF', 'DATA_2D_XY_NETCDF','DATA_3D_NETCDF','DATA_MASK_NETCDF_M01', \
            'SURFACE_DATA_NETCDF','DATA_1D_TS_NETCDF_N02','DATA_1D_TS_NETCDF']

convention = 'dirpart'
file_prefix = ''
file_suffix = ''
create_new_file = True
offset_min = 0
part_timeshift = 0
variable_zlib = True
variable_complevel = 6
output_timestep = 0
configname = ''

# read configuration from command line
# line and parse it
def print_help():
    print('palm_joint_outputs.py -c <config name>')

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
if sys.argv[0].endswith('pydevconsole.py'):
    # debugging in pycharm
    runpath = os.path.join(os.path.abspath(os.path.curdir), 'util')
    configname = 'dejvice_validation_summer_e2_final'
else:
    # real run - we need connect current path with relative path to script
    runpath = os.path.dirname(os.path.abspath(os.path.join(os.path.abspath(os.path.curdir),sys.argv[0])))

if configname == '':
    # palm_jointoutputs requires domain and resolution
    print("palm_jointoutputs requires <config name>")
    print_help()
    exit(2)


# check supplied params of run
configfile = os.path.join(runpath, 'config', configname+'.conf')
if not os.path.isfile(configfile):
    print("Config file "+configfile+" does not exists!")
    print_help()
    exit(2)

# read domain configuration
exec(open(configfile).read())

print('Join files start: ', datetime.now())
print('Config file: ', configfile)
print('Origin path: ', origpath)
print('Output path: ', finalpath)
print('Processed files: ', filelist)
print('File prefix: ', file_prefix)
print('File suffix: ', file_suffix)
print('Parts convention:', convention)
print('Timeshift of parts:', part_timeshift)
print('Create new output file:', create_new_file)


# returns filename of the base part
def filename(origpath, file, convention):
    if convention == 'dirpart':
        return os.path.join(origpath, file + file_suffix)
    elif convention == 'filepart':
        return os.path.join(origpath, file + file_suffix)
    elif convention == 'tmpdir':
        return os.path.join(origpath, file + file_suffix)
    elif convention == 'filenum':
        return os.path.join(origpath, file + '.000' + file_suffix)
    elif convention == 'singlefile':
        return os.path.join(origpath, file + file_suffix)

# returns filenames of the parts
def partnames(origpath, origfile, convention):
    parts = []
    if convention == 'dirpart':
        parts.extend(glob.glob(os.path.join(origpath + '.part*', origfile + file_suffix)))
        parts.sort()
        parts.insert(0, os.path.join(origpath, origfile + file_suffix))
    elif convention == 'filepart':
        parts.extend(glob.glob(os.path.join(origpath, origfile + '.part*' + file_suffix)))
        parts.sort()
        parts.insert(0, os.path.join(origpath, origfile + file_suffix))
    elif convention == 'tmpdir':
        parts.extend(glob.glob(os.path.join(origpath + '.*', file + file_suffix)))
        parts.sort()
        # parts.insert(0, os.path.join(origpath, file + file_suffix))
    elif convention == 'filenum':
        parts.extend(glob.glob(os.path.join(origpath, origfile + '.*' + file_suffix)))
        parts.sort()
    elif convention == 'palmrun':
        parts.extend(glob.glob(os.path.join(origpath, file_prefix + origfile + '.*' + file_suffix)))
        parts.sort()
    elif convention == 'filepattern':
        print('Origpath:', origpath)
        print('Parts:', file_prefix + origfile + file_suffix + '*')
        parts.extend(glob.glob(os.path.join(origpath, file_prefix + origfile + file_suffix + '*')))
        parts.sort()
    elif convention == 'singlefile':
        parts = [os.path.join(origpath, file + file_suffix)]
    print(parts)
    return parts

def nc_copy_structure(nc_in, nc_out):
    # nc_in        #> file handler of input netcdf
    # nc_out       #> file handler of output netcdf
    ok = False
    try:
        # copy global attributes
        for attr_in in nc_in.ncattrs():
            nc_out.setncattr(attr_in, nc_in.getncattr(attr_in))
        for dn in nc_in.dimensions:
            d = nc_in.dimensions[dn]
            print('Create dimension:', d.name, d.size)
            if dn == 'time':
                nc_out.createDimension(d.name, None)
            else:
                nc_out.createDimension(d.name, d.size)
        for vn in nc_in.variables:
            print('Create variable:', vn)
            v = nc_in.variables[vn]
            # copy values of time-invariant variables
            if len(v.dimensions) == 0:
                nc_out.createVariable(vn, v.datatype, v.dimensions)
                nc_out[vn].setncatts(nc_in[vn].__dict__)
                nc_out[vn][:] = nc_in[vn][:]
            elif v.dimensions[0] != 'time':
                nc_out.createVariable(vn, v.datatype, v.dimensions)
                nc_out[vn].setncatts(nc_in[vn].__dict__)
                if len(v.dimensions) == 1:
                    nc_out[vn][:] = nc_in[vn][:]
                elif len(v.dimensions) == 2:
                    nc_out[vn][:,:] = nc_in[vn][:,:]
                elif len(v.dimensions) == 3:
                    nc_out[vn][:,:,:] = nc_in[vn][:,:,:]
                else:
                    print('Too many dimensions in variable', vn)
            elif vn == 'time':
                nc_out.createVariable(vn, v.datatype, v.dimensions)
                nc_out[vn].setncatts(nc_in[vn].__dict__)
            else:
                if v.datatype == np.float32:
                    nc_out.createVariable(vn, v.datatype, v.dimensions, zlib=variable_zlib, complevel=variable_complevel, fill_value=-9999.0)
                    nc_out[vn].setncatts(nc_in[vn].__dict__)
                else:
                    nc_out.createVariable(vn, v.datatype, v.dimensions, zlib=variable_zlib, complevel=variable_complevel)
                    nc_out[vn].setncatts(nc_in[vn].__dict__)
        ok = True
    except Exception as exo:
        print("Error copy output nc file: {0}".format(exo))
    finally:
        return ok


# #### loop over files ###
for file in filelist:
    # file = filelist[0]
    print('Processing file:', file)

    # get list of parts
    parts = partnames(origpath, file, convention)
    # get output file path and name
    fout = os.path.join(finalpath, file_prefix + file)
    print('Out file:',fout)
    if create_new_file:
        #check output directory
        if not os.path.exists(finalpath):
            os.makedirs(finalpath)
        # create output file
        nc_out = Dataset(fout, "w", format="NETCDF4")
        # copy the structure of the main file from the first part
        nc_in = Dataset(parts[0], "r", format="NETCDF4")
        if not nc_copy_structure(nc_in, nc_out):
            print('Problem creating of the nc file structure of output nc file')
            sys.exit(1)
        nc_in.close()
    else:
        # open output nc file
        nc_out = Dataset(fout, "a", format="NETCDF4")
    # analyze the output file
    vars = nc_out.variables
    vcp = []
    for v in vars:
        if len(vars[v].dimensions) > 1 or (len(vars[v].dimensions) == 1 and vars[v].dimensions[0] == 'time'):
            if vars[v].dimensions[0] == 'time':
                vcp.append(v)
    print('Variables to copy:', vcp)

    # get list of timesteps in individual files
    pinfo = {}
    for ip in range(len(parts)):
        part = parts[ip]
        ptshift = ip * part_timeshift
        print('Analyzing file', ip, part, ptshift)
        # open nc file
        ncp = Dataset(part, "r", format="NETCDF4")
        # get time steps of the part file
        ptsteps = []
        ptime = ncp.variables['time']
        # find timestep offset, skip masked steps
        offset = offset_min
        for i in range(len(ptime)):
            if not ptime[i].mask:
                offset = max(offset_min, i)
                break
        if offset is not None:
            for i in range(offset,len(ptime)):
                if ptime[i].mask:
                    break
                ptsteps.append(ptime[i].data.item(0))
            # check rest of the timesteps
            for i in range(offset+len(ptsteps),len(ptime)):
                if not ptime[i].mask:
                    # print warning
                    print('WARNING: Discontinuous timestep:',i, ptime[i], 'in file', part)
        if len(ptsteps) > 0:
            pinfo[part] = {}
            pinfo[part]['nts'] = len(ptsteps)
            pinfo[part]['file'] = part
            pinfo[part]['ptsteps'] = ptsteps
            pinfo[part]['offset'] = offset
            pinfo[part]['ptshift'] = ptshift
        ncp.close()
    # arrange timesteps into final file
    tsteps = set()
    for part in pinfo:
        tsteps = tsteps.union(set(pinfo[part]['ptsteps']))
    tsteps2 = list(tsteps)
    tsteps2.sort()
    # remove duplicite timesteps (duplicate inside the range of 1s, keep the last one)
    for i in range(len(tsteps2)):
        if i == 0:
            tsteps = [tsteps2[0]]
        elif abs(tsteps2[i] - tsteps2[i-1]) < output_timestep/2.0:
            # timestep in the same range - replace
            tsteps[len(tsteps)-1] = tsteps2[i]
        else:
            # new one - append
            tsteps.append(tsteps2[i])
    # remove intermediate timesteps according prescribed output_timestep
    output_timestep = int(output_timestep)
    if output_timestep > 1:
        tsteps2 = tsteps
        tsteps = []
        for i in range(len(tsteps2)):
            if int(tsteps2[i]) - int(tsteps2[i]/output_timestep)*output_timestep < 1:
                # new one - append
                tsteps.append(tsteps2[i])
    # match part ts to global ts
    for part in pinfo:
        print('Matching tsteps of part to global ts:', part)
        ptsteps = pinfo[part]['ptsteps']
        # find first matching part
        for tstep in ptsteps:
             if tstep in tsteps:
                break
        # !! add check and removal of parts with empty contribution !!!
        print('Starting ts:',
              tstep, ptsteps.index(tstep), pinfo[part]['offset'],
              ptsteps.index(tstep) + pinfo[part]['offset'], tsteps.index(tstep))
        pinfo[part]['ptsmin'] = ptsteps.index(tstep) + pinfo[part]['offset']
        pinfo[part]['tsmin'] = tsteps.index(tstep)
        # find last matching part
        for tstep in ptsteps[ptsteps.index(tstep):]:
            if tstep not in tsteps:
                break
        if tstep not in tsteps:
            # should not arise
            print('Part timestep ', tstep, ' not in output timesteps - something wrong?')
            print(part)
            tstep = ptsteps[ptsteps.index(tstep)-1]
        print('Ending ts:', tstep, ptsteps.index(tstep), pinfo[part]['offset'],
              ptsteps.index(tstep) + pinfo[part]['offset'], tsteps.index(tstep))
        pinfo[part]['ptsmax'] = ptsteps.index(tstep) + pinfo[part]['offset']
        pinfo[part]['tsmax'] = tsteps.index(tstep)

    # processing selected timesteps into the final file
    # open final file for editing
    vars = nc_out.variables
    # process selected parts
    for part in pinfo:
        pi = pinfo[part]
        print('Processing file', pi['file'])
        print('Timesteps range:', pi['ptsmin'],pi['ptsmax'])
        # open part nc file
        ncp = Dataset(pi['file'], "r", format="NETCDF4")
        pvars = ncp.variables
        # copy timesteps and variables
        print('Copy range of timesteps:', pi['ptsmin'],':',pi['ptsmax']+1, ', ', pi['tsmin'],':',pi['tsmax']+1)
        # add ptimes to time dimension of the main file
        print('Copied times:',pvars['time'][pi['ptsmin']:pi['ptsmax']+1])
        times = pvars['time'][pi['ptsmin']:pi['ptsmax']+1] + pi['ptshift']
        print('Copy into times:', times)
        print('Copy into ts:', pi['tsmin'], ":", pi['tsmax']+1)
        vars['time'][pi['tsmin']:pi['tsmax']+1] = times
        print('vars[time]:', vars['time'][pi['tsmin']:pi['tsmax']+1])
        # copy all variables
        for v in vcp:
            if v not in pvars:
                # Variable is not included in the part file
                print('Variable ', v, ' is not in part ',pi['file'])
                continue
            print('Copying variable ', v)
            nd = len(vars[v].dimensions)
            vs = vars[v].shape
            offset = pi['ptsmin'] - pi['tsmin']
            for i in range(pi['tsmin'], pi['tsmax']+1):
                if nd == 1:
                    vars[v][i] = pvars[v][i+offset]
                elif nd == 2:
                    vars[v][i,:] = pvars[v][i+offset,0:vs[1]]
                elif nd == 3:
                    vars[v][i,:,:] = pvars[v][i+offset,0:vs[1],0:vs[2]]
                elif nd == 4:
                    vars[v][i,:,:,:] = pvars[v][i+offset,0:vs[1],0:vs[2],0:vs[3]]
                elif nd == 5:
                    vars[v][i,:,:,:,:] = pvars[v][i+offset,0:vs[1],0:vs[2],0:vs[3],0:vs[4]]
                elif nd == 6:
                    vars[v][i,:,:,:,:,:] = pvars[v][i+offset,0:vs[1],0:vs[2],0:vs[3],0:vs[4],0:vs[5]]
                else:
                    print('Too many dimensions of variable',v,'! - skipping')
        # close part file
        ncp.close()

    # close final file
    nc_out.close()
    print('Join files end: ', datetime.now())
    print('File:', file, 'processed.')