"""Spatial segmentation module"""


import abc
from affine import Affine
import numpy as np
from rasterio import features
from django.contrib.gis.geos.geometry import GEOSGeometry

from madmex.util.spatial import feature_transform
from madmex.models import PredictObject

class BaseSegmentation(metaclass=abc.ABCMeta):
    """
    Parent class implementing generic methods related to running spatial segmentation
    algorithms on raster data, converting input and output data and interacting with the
    database.
    """
    def __init__(self, array, affine, crs):
        """Parent class to run spatial segmentation

        Args:
            array (numpy.array): A 3 dimensional numpy array (TODO: Specify dimension ordering)
            affine (affine.Affine): Affine transform
            crs (str): Proj4 string corresponding to the array's CRS
        """
        self.array = array
        self.affine = affine
        self.crs = crs
        self.fc = None
        self.segments_array = None
        self.algorithm = None

    @classmethod
    def from_geoarray(cls, geoarray):
        """Instantiate class from a geoarray (xarray read with datacube.load)

        geoarray (xarray.Dataset): a Dataset with crs and affine attribute. Typically
            coming from a call to Datacube.load or GridWorkflow.load
        """
        array = geoarray.to_array().values
        affine = Affine(*list(geoarray.affine)[0:6])
        crs = geoarray.crs._crs.ExportToProj4()
        return cls(array=array, affine=affine, crs=crs)

    @abc.abstractmethod
    def segment(self):
        """Run segmentation
        """
        pass


    def polygonize(self, crs_out="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"):
        """Transform the raster result of a segmentation to a feature collection

        Args:
            crs_out (proj4): The coordinate reference system of the feature collection
                produced. Defaults to longlat, can be None if no reprojection is needed
        """
        if self.segments_array is None:
            raise ValueError("self.segments_array is None, you must run segment before this method")
        # Use rasterio.features.shapes to generate a geometries collection from the
        # segmented raster
        geom_collection = features.shapes(self.segments_array.astype(np.uint16),
                                          transform=self.affine)
        # Make it a valid featurecollection
        def to_feature(feature):
            """Tranforms the results of the results of rasterio.feature.shape to a feature"""
            fc_out = {
                "type": "Feature",
                "geometry": {
                    "type": feature[0]['type'],
                    "coordinates": feature[0]['coordinates']
                },
                "properties": {
                    "id": feature[1]
                }
            }
            return fc_out
        fc_out = [to_feature(x) for x in geom_collection]
        if crs_out is not None:
            fc_out = [feature_transform(x, self.crs, crs_out) for x in fc_out]
        self.fc = fc_out

    def _get_params(self):
        """Retrieve segmentation parameters and dumps them to a json string

        Used for registering metadata together with geometries to the database
        """
        pass

    def to_db(self, year, data_source):
        """Write the result of a segmentation to the database

        Args:
            year (int): Year of the data used for the segmentation
            data_source (str): Identifier for the data used as input for this segmentation

        """
        if self.fc is None:
            raise ValueError('fc (feature collection) attribute is empty, you must first run the polygonize method')

        # TODO: Retrieve param string using self._get_params, and implement writing to table params, algorithm, datasource and year

        def predict_obj_builder(x):
            geom = GEOSGeometry(json.dumps(x['geometry']))
            obj = PredictObject(the_geom=geom)
            return obj

        obj_list = [predict_obj_builder(x) for x in self.fc]
        PredictObject.objects.bulk_create(obj_list)


