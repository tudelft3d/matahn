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

import subprocess32 as subprocess
from matahn import app

def lasmerge(filenames, x_min, y_min, x_max, y_max, classes, outname):
    q = [app.config['LASMERGE_BINARY'], '-keep_class', classes.replace(',', ' '), '-inside', str(x_min), str(y_min), str(x_max), str(y_max), '-olaz', '-o', outname, '-i'] + filenames
    subprocess.check_call(q)
    return outname

def lasinfotxt(filename):
    subprocess.check_call([app.config['LASINFO_BINARY'], '-nmm', '-nv', '-nc', filename, '-otxt'])
    return filename[:-3]+'txt'

