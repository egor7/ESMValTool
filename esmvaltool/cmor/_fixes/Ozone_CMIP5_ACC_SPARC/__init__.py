"""General fix for all models of project Ozone_CMIP5_ACC_SPARC."""
import cf_units
import numpy as np


def fix_time_coordinate(cube):
    """Fix time coordinate of Ozone_CMIP5_ACC_SPARC cubes.

    Change units of time axis from `months since ...` to `days since ...` and
    round to months if necessary.

    Parameters
    ----------
    cube: iris.cube.Cube

    Returns
    -------
    iris.cube.Cube

    """
    time = cube.coord('time')
    time.convert_units('days since 1850-01-01 00:00:00')
    new_array = np.copy(time.points)
    for idx in range(time.shape[0]):
        point = time.cell(idx).point
        if point.day >= 15:
            new_month = point.month % 12 + 1
            if new_month == 1:
                new_year = point.year + 1
            else:
                new_year = point.year
            new_time = point.replace(
                year=new_year, month=new_month, day=1, hour=0, minute=0)
            new_array[idx] = cf_units.date2num(new_time, time.units.name,
                                               time.units.calendar)
    time.points = new_array
    return cube