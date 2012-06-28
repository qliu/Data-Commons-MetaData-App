"""=============================================================================
util.py

General Unilities for the Web App
============================================================================="""

from django.conf import settings
from django.utils import simplejson

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

import os
import csv

# Import Regular Expression operations
import re

# Import the ElementTree XML API for Python
#import elementtree.ElementTree as ET
from xml.etree import ElementTree


# GLOBAL VARIABLES
## File size precision for human readable presentation of file size in bytes
FILE_SIZE_PRECISION = 0

## No data value for NULL value strings in table
NO_DATA_VALUE = "No Data"

## File extensions accociated with shaplefile
SHAPEFILE_EXTENSION = ["shp","dbf","prj","sbn","sbx","shp.xml","shx"]


# Source Data Lookup Table CSV file path
LOOKUP_TABLE_ROOT_PATH = 'C:/QLiu/ql_dj/apps/Data-Commons-MetaData-App/data/source_data/lookup_tables/'
##Standard lookup table path (containing only two fields: id and name)
STANDARD_LOOKUP_TABLES = ["coverage","geography","macrodomain","subjectmatter","source"]
##Other lookup table path
LOOKUP_TABLE_FORMAT = "format"

# Source Data Inventory CSV file path
SOURCE_DATA_INVENTORY_PATH = 'C:/QLiu/ql_dj/apps/Data-Commons-MetaData-App/data/source_data/original_data/PitonDataInventory2012.csv'

# Source Data Root Path in Inventory File
SOURCE_DATA_ROOT_PATH_ORIGIN = 'G:\\'

# Source Data Root Path Mapped Locally
#SOURCE_DATA_ROOT_PATH_LOCAL = 'O:\\Data\\'

# Source Data Root Path On Server "Pitondc1"
SOURCE_DATA_ROOT_PATH_LOCAL = '\\\\pitondc1\\Departments\\Data\\'


# Decorator to save time returning templates
def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response 
    function with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

# Convert file size to human readable presentation of a number of bytes
def HumanReadableSize(size,precision):
    suffixes = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    suffix_index = 0
    while size >= 1024:
        suffix_index += 1
        size /= 1024.0
    return "%.*f %s" % (precision,size,suffixes[suffix_index])

# Clean NULL value for strings in table when uploading from CSV file
def CleanNullValue(value):
    return NO_DATA_VALUE if value=="" else value

# Get total file size for directory
def GetDirSize(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

# Get file size for all possible extensions
def GetFileSize(file_path,extensions):
    file_size = 0
    for extension in extensions:
        file_full_path = file_path+".%s" % extension
        if os.path.exists(file_full_path):
            file_size = os.path.getsize(file_full_path)
    return file_size

# Get total file size for shapefile and accociated files (.shp,.dbf,.prj,.sbn,.sbx,.shp.xml,.shx)
def GetShapefileSize(file_path):
    file_size = 0
    for extension in SHAPEFILE_EXTENSION:
        file_full_path = file_path+".%s" % extension
        if os.path.exists(file_full_path):
            file_size += os.path.getsize(file_full_path)
    return file_size
