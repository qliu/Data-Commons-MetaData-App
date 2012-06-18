from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import models

# Import from general utilities
from util import *

from dcmetadata.models import *

import os
import csv

# Source Data Inventory CSV file path
SOURCE_DATA_INVENTORY_PATH = 'C:/QLiu/ql_dj/apps/Data-Commons-MetaData-App/data/source_data/original_data/PitonDataInventory2012.csv'

# Source Data Root Path in Inventory File
SOURCE_DATA_ROOT_PATH_ORIGIN = 'G:\\'

# Source Data Root Path Mapped Locally
SOURCE_DATA_ROOT_PATH_LOCAL = 'O:\\Data\\'

# Test
def test(request):
    with open('c:/tmp/testfile.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            print row[1]
            size = os.path.getsize(row[1])
            print size
            print HumanReadableSize(size,0)
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
                # get file location
                file_location = row[10].replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)
                # get file size
                file_size = os.path.getsize(file_location)
                # get begin year, end year
                str_year = row[5]
                list_year = str_year.split('-')
                if str_year != "" and str_year != "?" and str_year != "NA":
                    begin_year = int(list_year[0])
                    end_year = int(list_year[1 if len(list_year)==2 else 0])
                else:
                    begin_year = None
                    end_year = None
                
                # load inventory file into model instance    
                source_data = SourceDataInventory(
                    inventory_id=row[0],
                    file_name=row[1],
                    description=row[2],
                    macro_domain=MacroDomain.objects.get(name=Clean_Null_Value(row[3])),
                    subject_matter=SubjectMatter.objects.get(name=Clean_Null_Value(row[4])),
                    begin_year=begin_year,
                    end_year=end_year,
                    geography=Geography.objects.get(name=Clean_Null_Value(row[6])),
                    coverage=Coverage.objects.get(name=Clean_Null_Value(row[7])),
                    source=Source.objects.get(name=Clean_Null_Value(row[8])),
                    format=Format.objects.get(name=Clean_Null_Value(row[9])),
                    location=file_location,
                    file_size=file_size)
                source_data.save()
        return HttpResponse("Source Data Inventory - Upload complete!")
    except:
        return HttpResponse("Upload Failed!")
    
@render_to("dcmetadata/test_dajaxice.html")
def test_dajaxice(request):
    return {}