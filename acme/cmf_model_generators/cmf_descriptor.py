# -*- coding: utf-8 -*-
"""
Created on Nov 08 09:18 2017
@author(s): Florian U. Jehn, Philipp Kraft

Describes a cmf model with storages, connections, cells, forcing data,
outlets and so forth.
"""
import cmf


def describe(project: cmf.project, out):
    """
    Describes a cmf project in a file like object.

    :param project: cmf project
    :param out: filelike object
    :return: None
    """
    out.write('Project: {}\n'.format(project))

    out.write("\nCells:\n")
    for cell in project:
        out.write('\t- {}:\n'.format(cell))
        for storage in cell.storages:
            out.write('\t\t- {}\n'.format(storage))
            for connection in storage.connections:
                out.write('\t\t\t- {}\n'.format(connection))

    out.write("\nMeteo Stations:\n")

    # ### Is there a smarter way to do this?
    # P: Yes see below
    # Definition of all possible timeseries in meteo station
    for meteo in project.meteo_stations:
        out.write("\t- {}:\n".format(meteo))
        data_dict = meteo.TimeseriesDictionary()
        for variablename, timeseries in data_dict.items():
            if timeseries:
                out.write("\t\t{}:{}\n".format(variablename, timeseries))
                # Breaks if the timeseries does not exist. Therefore try; except
                mean_val = timeseries_object.mean()
                min_val = timeseries_object.min()
                max_val = timeseries_object.max()
                out.write("\t\t\t- Mean: {}\tMin: {}\tMax: {}\n".format(
                    mean_val, min_val, max_val
                ))
            else:
                out.write("\t\t{}: ~".format(variablename)

    out.write("\nRain Stations:\n")
    for rain in project.rainfall_stations:
        out.write("\t- {}:\n".format(rain))

    out.write("\nOutlets:\n")
    for outlet in project.nodes:
        out.write("\t- {}:\n".format(outlet))


