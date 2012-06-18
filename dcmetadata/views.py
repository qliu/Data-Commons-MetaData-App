from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import models

# Import from general utilities
from util import *

from dcmetadata.models import *


# Source Data Inventory CSV file path
SOURCE_DATA_INVENTORY_PATH = 'C:/QLiu/ql_dj/apps/Data-Commons-MetaData-App/data/source_data/original_data/PitonDataInventory2012.csv'

# Source Data Root Path in Inventory File
SOURCE_DATA_ROOT_PATH_ORIGIN = 'G:\\'

# Source Data Root Path Mapped Locally
SOURCE_DATA_ROOT_PATH_LOCAL = 'O:\\Data\\'

# Test
def test(request):
    file_location = "O:\Data\Source Data\CensusBureau\2010\SF1 Data"
    file_name = "Census_Bureau_raw_download"
    file_path = os.path.join(file_location,file_name)

    total_size = 0
    for root, dirs, files in os.walk(file_path):
        for fname in files:
            fpath = os.path.join(root,fname)
            if os.path.exists(fpath):
                total_size += os.path.getsize(fpath)
    return HttpResponse("test done!")

# Upload source data inventory CSV file into PostgreSQL database
def upload_sourcedata(request):
    '''
    Upload source data inventory from csv file
    '''
    try:
        with open(SOURCE_DATA_INVENTORY_PATH,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                # get begin year, end year
                str_year = row[5]
                list_year = str_year.split('-')
                if str_year != "" and str_year != "?" and str_year != "NA":
                    begin_year = int(list_year[0])
                    end_year = int(list_year[1 if len(list_year)==2 else 0])
                else:
                    begin_year = None
                    end_year = None
                # get file location
                file_location = row[10].replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)                
                # get file size
                file_name = row[1]
                file_path = os.path.join(file_location,file_name)
                str_format = row[9]
                file_format = Format.objects.get(name=CleanNullValue(str_format))
                extensions = file_format.extension.split(';') #get all possible extensions for the file format
                ##calculate file size for directory
                if str_format == "File folder":
                    file_size = GetDirSize(file_path)
                ##calculate file size for HTML files
                elif str_format == "HTML link":
                    file_size = GetFileSize(file_path,extensions)
                    html_files_path = file_path + "_files"
                    if os.path.exists(html_files_path):#if HTML file has a file folder accociated with it
                        file_size += GetDirSize(html_files_path)
                ##calculate file size for shapefiles
                elif str_format == "Shapefile":
                    file_size = GetShapefileSize(file_path)
                ##calculate file size for other formats
                else:
                    file_size = GetFileSize(file_path,extensions)
                    
                # load inventory file into model instance    
                source_data = SourceDataInventory(
                    inventory_id=row[0],
                    file_name=file_name,
                    description=row[2],
                    macro_domain=MacroDomain.objects.get(name=CleanNullValue(row[3])),
                    subject_matter=SubjectMatter.objects.get(name=CleanNullValue(row[4])),
                    begin_year=begin_year,
                    end_year=end_year,
                    geography=Geography.objects.get(name=CleanNullValue(row[6])),
                    coverage=Coverage.objects.get(name=CleanNullValue(row[7])),
                    source=Source.objects.get(name=CleanNullValue(row[8])),
                    format=file_format,
                    location=file_location,
                    file_size=file_size)
                source_data.save()
        return HttpResponse("Source Data Inventory - Upload complete!")
    except:
        return HttpResponse("Upload Failed!")
    
@render_to("dcmetadata/test_dajaxice.html")
def test_dajaxice(request):
    return {}