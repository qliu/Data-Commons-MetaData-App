from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import models
from django.db.models.loading import get_model

# Import from general utilities
from util import *

from dcmetadata.models import *
from dcmetadata.forms import *

# Test
def test(request):
    print "*" * 100
    q = 'mdb'
    test_format = Format.objects.extra(
        where=['ext_tsv @@ plainto_tsquery(%s)'],params=[q])
    print test_format
    print "*" * 100

    return HttpResponse("test done!")

# Upload standard lookup tables (containing only two fields: id and name) CSV file into PostgreSQL database
def upload_standard_lookup_tables(request):
    return_http_string = ""
    try:
        for table in STANDARD_LOOKUP_TABLES:
            lookup_table_path = LOOKUP_TABLE_ROOT_PATH + table + ".csv"
            with open(lookup_table_path,'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    lookup_table = get_model("dcmetadata",table)(
                        id=row[0],
                        name=row[1]
                    )
                    lookup_table.save()
                return_http_string = return_http_string + "Lookup Table " + table + " - Upload Complete! <br/>"
        return HttpResponse(return_http_string)
    except:
        return HttpResponse("Upload Failed!")
    
# Upload other lookup tables
def upload_lookup_table_format(request):
    table = "format"
    try:
        lookup_table_path = LOOKUP_TABLE_ROOT_PATH + table + ".csv"
        with open(lookup_table_path,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                lookup_table = get_model("dcmetadata",table)(
                    id=row[0],
                    name=row[1],
                    extension=row[2]
                )
                lookup_table.save()
        return HttpResponse("Lookup Table " + table + " - Upload Complete!")
    except:
        return HttpResponse("Upload Failed!")

# Upload source data inventory CSV file into PostgreSQL database
def upload_sourcedata(request):
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
                    id=row[0],
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

'''------------
Metadata
------------'''

# Display Metadata Entry
@render_to("dcmetadata/metadata_detail.html")
def metadata_detail(request,metadata_id):
    metadata = Metadata.objects.get(id=metadata_id)
    metadata_xml = metadata.metadata
    metadata_list = metadata._get_metadata_dict()
    metadata_fields = metadata_list[0]
    metadata_other = metadata_list[1]
    return {'metadata_id':metadata_id,'metadata_xml':metadata_xml,
            'metadata_fields':metadata_fields,
            'metadata_other':metadata_other,
            }

# Edit Metadata Entry
@render_to("dcmetadata/metadata_edit.html")
def metadata_edit(request,metadata_id):
    metadata =  Metadata.objects.get(id=metadata_id)
    metadata_xml = metadata.metadata
    metadata_form = MetadataFieldForm()
    
    return {'metadata_id':metadata_id,
            'metadata_form':metadata_form,
            'metadata_xml':metadata_xml,
    }
    
    
#    image_is_exist = True
#    
#    try:
#        img = Imagery.objects.get(id=img_no)
#    except:            
#        # fetch ids
#        imgid=[]
#        image_is_exist = False
#        id = Imagery.objects.values_list('id',flat=True)    
#        for i in id:
#            imgid.append(i)
#        if not imgid:
#            img_no = 1
#        else:
#            img_no = max(imgid)+1
#        img = Imagery(id=img_no)
#    if request.method == 'GET':
#        if img:
#            imgform = ImageForm(instance=img)
#        else:
#            initial = {}
#            initial['id'] = img_no
#            imgform = ImageForm(initial=initial)
#    
#    elif request.method == 'POST':
#        imgform = ImageForm(data=request.POST, instance=img)
#        if imgform.is_valid():
#            imgform.save()
#            return HttpResponseRedirect('/SWFWMD/imagerydb/imagery/%s/' % imgform.cleaned_data['id'])
#    
#    return {'img_no': img_no,'form': imgform,'image_is_exist':image_is_exist,}

# Delete Metadata Entry
## Metadata entry delete confirm
@render_to("dcmetadata/metadata_delete_confirm.html")
def metadata_delete_confirm(request,metadata_id):
    return {'metadata_id':metadata_id,
            }

## Delete Metadata entry
def metadata_delete(request,metadata_id):
    try:
        metadata = Metadata.objects.get(id=metadata_id)
    except:
        return HttpResponse("Metadata ID %s dose not exist." % metadata_id)
    
    metadata.delete()
    return HttpResponseRedirect('/admin/dcmetadata/metadata/')