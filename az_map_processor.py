import csv
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import json

def create_poly_dict(region_file):
    rv = {}
    with open(region_file) as json_file:
        region_dict = json.load(json_file)
        for region, point_list in region_dict.items():
            tupled_list = []
            for lst in point_list:
                tupled_sublst = []
                for point in lst:
                    tupled_sublst.append(tuple(reversed(point[:2])))
                tupled_list.append(tupled_sublst)

            rv[region] = Polygon(tupled_list)
    return rv


def process_input(input_file, num_new, include_all=False):
    '''
    processes the locations in an input file

    Inputs:
        input_file: the filename to open (str)
        num_new: number of new locations expected
        include_all: defaults to False

    Returns: a list of locations
    '''

    loc_list = []
    with open(input_file, 'r') as file:
        csvreader = csv.reader(file)
        for loc in csvreader:
            clean_loc = []
            for coord in loc:
                clean_loc.append(float(coord))
            loc_list.append(clean_loc)
    
    if not include_all:
        return loc_list[len(loc_list) - num_new:]

    return loc_list

def find_region(loc, region_poly_dict):
    point = Feature(geometry=Point(tuple(loc)))
    for region, poly in region_poly_dict.items():
        if boolean_point_in_polygon(point, poly):
            return region
    return 'NONE'

import click

@click.command()
@click.option('--locs-csv-file', type=str)
@click.option('--num-new', type=int)
@click.option('--include-all', type=bool)
@click.option('--region-file', type=str)
@click.option('--output-file', type=str)

def cmd(locs_csv_file, num_new, include_all, region_file, output_file):
    poly_dict = create_poly_dict(region_file)
    loc_list = process_input(locs_csv_file, num_new, include_all)
    output_list = []
    for loc in loc_list:
        url = 'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint='\
         + str(loc[0]) + '%2C' + str(loc[1])
        output_list.append([url, find_region(loc, poly_dict), None, loc[0], loc[1]])
    with open(output_file, 'w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerows(output_list)

if __name__ == '__main__':
    cmd()