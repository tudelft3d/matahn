# This file is part of MATAHN.

# MATAHN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MATAHN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MATAHN.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2014 Ravi Peters, Hugo Ledoux

import subprocess
from matahn import app

def run_command(q):
    #if app.debug:
    print(' '.join(q))
    subprocess.check_call(q)

def lasmerge(filenames, x_min, y_min, x_max, y_max, classes, outname):
    q = [app.config['LASMERGE_BINARY']]
    q += ['-keep_class'] + [str(c) for c in classes]
    q += ['-inside'] + [str(x_min), str(y_min), str(x_max), str(y_max)]
    q += ['-olaz', '-o'] + [outname]
    q += ['-rescale'] + ['0.01', '0.01', '0.01']
    q += ['-i'] + filenames
    run_command(q)
    return outname

def lasinfotxt(filename):
    q = [app.config['LASINFO_BINARY'], '-nmm', '-nv', '-nc', filename, '-otxt']
    run_command(q)
    return filename[:-3]+'txt'

