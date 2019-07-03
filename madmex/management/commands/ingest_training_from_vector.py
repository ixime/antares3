#!/usr/bin/env python

"""
Author: Loic Dutrieux
Date: 2018-08-30
Purpose: Ingest a vector file containing training data into the antares database
"""

import logging
import json
import os

from django.contrib.gis.geos.geometry import GEOSGeometry
import fiona
from fiona.crs import to_string
from pyproj import Proj

from madmex.management.base import AntaresBaseCommand
from madmex.models import TrainObject, Tag, TrainClassification
from madmex.util.spatial import feature_transform

logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    help = """
Ingest a vector file containing training data into the antares database

--------------
Example usage:
--------------
antares ingest_training_from_vector /path/to/file.shp --scheme madmex --year 2015 --name train_mexico --field code
    """
    def add_arguments(self, parser):
        parser.add_argument('input_file',
                            type=str,
                            help='Path of vector file to ingest')
        parser.add_argument('-scheme', '--scheme',
                            type=str,
                            help='Name of the classification scheme to which the data belong')
        parser.add_argument('-field', '--field',
                            type=str,
                            help='Name of the vector file field containing the numeric codes of the class of interest')
        parser.add_argument('-name', '--name',
                            type=str,
                            help='Name/identifier under which the training set should be registered in the database')
        parser.add_argument('-year', '--year',
                            type=str,
                            help='Data interpretation year',
                            required=False,
                            default=-1)
    def handle(self, **options):
        input_file = options['input_file']
        year = options['year']
        scheme = options['scheme']
        field = options['field']
        name = options['name']
        # Create ValidClassification objects list
        # Push it to database

        # Read file and Optionally reproject the features to longlat
        with fiona.open(input_file) as src:
            p = Proj(src.crs)
            if p.is_latlong(): # Here we assume that geographic coordinates are automatically 4326 (not quite true)
                fc = list(src)
            else:
                crs_str = to_string(src.crs)
                fc = [feature_transform(x, crs_out='+proj=longlat', crs_in=crs_str)
                      for x in src]

        # Write features to ValidObject table
        def train_obj_builder(x):
            """Build individual ValidObjects
            """
            geom = GEOSGeometry(json.dumps(x['geometry']))
            obj = TrainObject(the_geom=geom,
                              filename=os.path.basename(input_file),
                              creation_year=year)
            return obj

        obj_list = [train_obj_builder(x) for x in fc]
        batch_size = int(len(obj_list)/4)
        TrainObject.objects.bulk_create(obj_list, batch_size=batch_size)

        # Get list of unique tags
        unique_numeric_codes = list(set([x['properties'][field] for x in fc]))

        # Update Tag table using get or create
        def make_tag_tuple(x):
            obj, _ = Tag.objects.get_or_create(numeric_code=x, scheme=scheme)
            return (x, obj)

        tag_dict = dict([make_tag_tuple(x) for x in unique_numeric_codes])

        # Build validClassification object list (valid_tag, valid_object, valid_set)
        def train_class_obj_builder(x):
            """x is a tuple (ValidObject, feature)"""
            tag = tag_dict[x[1]['properties'][field]]
            obj = TrainClassification(predict_tag=tag,
                                      interpret_tag=tag,
                                      train_object=x[0],
                                      training_set=name)
            return obj

        train_class_obj_list = [train_class_obj_builder(x) for x in zip(obj_list, fc)]

        TrainClassification.objects.bulk_create(train_class_obj_list, batch_size=batch_size)
