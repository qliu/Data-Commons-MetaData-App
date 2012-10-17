from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import models
from django.db.models.loading import get_model

# Import from general utilities
from util import *

from dcmetadata.models import *
from dcmetadata.forms import *

# AJAX Admin get Subject Matter on selected Macro Domain
def ajax_get_subjectmatter(request):
    print "#" * 100
    if request.is_ajax() and request.method == 'POST':
        macrodomain_id = int(request.POST.get('macrodomain',''))
        subjectmatters = SubjectMatter.objects.filter(macrodomain=macrodomain_id)
    return HttpResponse(subjectmatters,mimetype="text/plain")

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
                    year = int(list_year[0])
#                    begin_year = int(list_year[0])
#                    end_year = int(list_year[1 if len(list_year)==2 else 0])
                else:
                    year = None
#                    begin_year = None
#                    end_year = None
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
                    year=year,
#                    begin_year=begin_year,
#                    end_year=end_year,
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

# Copy table tags from source data attributes
def maketabletags(request):
#    try:
        source_data = SourceDataInventory.objects.all()
        
        # Build JSON Structure
        json_metadata = ""
        json_field_metadata = []
        
        for sd in source_data:
            metadata_id = sd.id
            if len(TableMetadata.objects.filter(id=metadata_id)) == 0:
                json_table_tags = {"geography":sd.coverage.name,
                                   "geographic_level":sd.geography.name,
                                   "domain":sd.macro_domain.name,
                                   "subdomain":sd.subject_matter.name,
                                   "source":sd.source.name,
                                   "year":sd.year
#                                   "time_period":"%d;%d" % (sd.begin_year if sd.begin_year != None else 0,sd.end_year if sd.end_year != None else 0)
                                  }
                json_field_metadata_tags = {}
                json_root_dict = {"table_tags":json_table_tags,
                                  "field_metadata":json_field_metadata
                                }            
                json_metadata = json.dumps(json_root_dict)
                output_metadata = TableMetadata(id=metadata_id,metadata=json_metadata)
                output_metadata.save()
            
        return HttpResponse("Copy Table Tags from Source Data Inventory - Complete!")
#    except:
#        return HttpResponse("Copy Table Tags from Source Data Inventory - Failed!")        

# Convert XML metadata to JSON metadata
def xml2json(request):
    try:
        metadata = Metadata.objects.all()
        
        for md in metadata:
            # Build JSON Structure
            json_metadata = ""
            json_field_metadata = []
            
            metadata_id = md.id
            print metadata_id

            # Table tags come from "source_data" attributes
            source_data = SourceDataInventory.objects.get(id=metadata_id)
            json_table_tags = {"geography":source_data.coverage.name,
                               "geographic_level":source_data.geography.name,
                               "domain":source_data.macro_domain.name,
                               "subdomain":source_data.subject_matter.name,
                               "source":source_data.source.name,
                               "year":source_data.year
#                               "time_period":"%d;%d" % (source_data.begin_year if source_data.begin_year != None else 0,source_data.end_year if source_data.end_year != None else 0)
                              }
            
            tree = ElementTree.ElementTree(ElementTree.fromstring(md.metadata))
            root = tree.getroot()
            for field in root[0]:   
                json_field_metadata_tags = {"geography":json_table_tags["geography"],
                                            "geographic_level":json_table_tags["geographic_level"],
                                            "domain":"",
                                            "subdomain":"",
                                            "year":"year",
#                                            "time_period":"",
                                            "visualization_types":[],
                                            "geometry":json_table_tags["geometry"]
                                            }     
                json_field_metadata_dict = {"field_name":field[0].text,
                                            "data_type":re.sub(r'[\t\n\r]','',field[1].text) if field[1].text != None else '',
                                            "verbose_name":re.sub(r'[\t\n\r]','',field[2].text) if field[2].text != None else '',
                                            "no_data_value":None,
                                            "tags":json_field_metadata_tags
                                            }
                json_field_metadata.append(json_field_metadata_dict)
                
            json_root_dict = {"table_tags":json_table_tags,
                              "field_metadata":json_field_metadata
                            }
            json_metadata = json.dumps(json_root_dict)
            
            output_metadata = Metadata(id=metadata_id,metadata=md.metadata,metadata_json=json_metadata)
            output_metadata.save()
            
        return HttpResponse("XML to JSON - Conversion complete!")
    except:
        return HttpResponse("XML to JSON - Conversion Failed!")

# Convert name to id for foreign keys in table metadata
def fkeyname2id(request):
    metadata_json = ""
    try:
        table_metadata = TableMetadata.objects.all()
        for tm in table_metadata:
            metadata_id = tm.id
            metadata_json_dict = tm._get_metadata_dict()
            table_tags = metadata_json_dict["table_tags"]
            field_metadata = metadata_json_dict["field_metadata"]
            
            # Convert name to id for table_tags
            table_tags["geography"] = Coverage.objects.get(name=table_tags["geography"]).id if table_tags["geography"].strip() != "" else 0
            table_tags["geographic_level"] = Geography.objects.get(name=table_tags["geographic_level"]).id if table_tags["geographic_level"].strip() != "" else 0
            table_tags["domain"] = MacroDomain.objects.get(name=table_tags["domain"]).id if table_tags["domain"].strip() != "" else 0
            table_tags["subdomain"] = SubjectMatter.objects.get(name=table_tags["subdomain"]).id if table_tags["subdomain"].strip() != "" else 0
            table_tags["source"] = Source.objects.get(name=table_tags["source"]).id if table_tags["source"].strip() != "" else 0
            
            # Convert name to id for field_metadata
            for fm in field_metadata:
                field_tags = fm["tags"]
                field_tags["geography"] = Coverage.objects.get(name=field_tags["geography"]).id if field_tags["geography"].strip() != "" else 0
                field_tags["geographic_level"] = Geography.objects.get(name=field_tags["geographic_level"]).id if field_tags["geographic_level"].strip() != "" else 0
                field_tags["domain"] = MacroDomain.objects.get(name=field_tags["domain"]).id if field_tags["domain"].strip() != "" else 0
                field_tags["subdomain"] = SubjectMatter.objects.get(name=field_tags["subdomain"]).id if field_tags["subdomain"].strip() != "" else 0
                visualization_types = []
                for vt in field_tags["visualization_types"]:
                    vt = VisualizationType.objects.get(name=vt).id if vt.strip() != "" else 0
                    visualization_types.append(vt)
                field_tags["visualization_types"] = visualization_types
            
            metadata_json = json.dumps(metadata_json_dict)
            output_metadata = TableMetadata(id=metadata_id,metadata=metadata_json)
            output_metadata.save()
        return HttpResponse("Foreign Key name to id - Conversion complete!")
    except:
        return HttpResponse("Foreign Key name to id - Conversion Failed!")


# Convert id to name for foreign keys in table metadata
def fkeyid2name(request):
    metadata_json = ""
    try:
        table_metadata = TableMetadata.objects.all()
        for tm in table_metadata:
            metadata_id = tm.id
            print "metadata id=%i" % metadata_id
            metadata_json_dict = tm._get_metadata_dict()
            table_tags = metadata_json_dict["table_tags"]
            field_metadata = metadata_json_dict["field_metadata"]
            
            # Convert id to name for table_tags
            table_tags["geography"] = Coverage.objects.get(id=int(table_tags["geography"])).name if table_tags["geography"] != 0 and table_tags["geography"] != None else ""
            table_tags["geographic_level"] = Geography.objects.get(id=int(table_tags["geographic_level"])).name if table_tags["geographic_level"] != 0 and table_tags["geographic_level"] != None else ""
            table_tags["domain"] = MacroDomain.objects.get(id=int(table_tags["domain"])).name if table_tags["domain"] != 0 and table_tags["domain"] != None else ""
            table_tags["subdomain"] = SubjectMatter.objects.get(id=int(table_tags["subdomain"])).name if table_tags["subdomain"] != 0 and table_tags["subdomain"] != None else ""
            table_tags["source"] = Source.objects.get(id=int(table_tags["source"])).name if table_tags["source"] != 0 and table_tags["source"] != None else ""
            
            # Convert id to name for field_metadata
            for fm in field_metadata:
                field_tags = fm["tags"]
                field_tags["geography"] = Coverage.objects.get(id=int(field_tags["geography"])).name if field_tags["geography"] != 0 and field_tags["geography"] != None else ""
                field_tags["geographic_level"] = Geography.objects.get(id=int(field_tags["geographic_level"])).name if field_tags["geographic_level"] != 0 and field_tags["geographic_level"] != None else ""
                field_tags["domain"] = MacroDomain.objects.get(id=int(field_tags["domain"])).name if field_tags["domain"] != 0 and field_tags["domain"] != None else ""
                field_tags["subdomain"] = SubjectMatter.objects.get(id=int(field_tags["subdomain"])).anme if field_tags["subdomain"] != 0 and field_tags["subdomain"] != None else ""
                visualization_types = []
                for vt in visualization_types:
                    vt = VisualizationType.objects.get(id=int(vt)).name if vt != 0 and vt != None else ""
                    visualization_types.append(vt)
                field_tags["visualization_types"] = visualization_types
                
            metadata_json = json.dumps(metadata_json_dict)
            output_metadata = TableMetadata(id=metadata_id,metadata=metadata_json)
            output_metadata.save()
        return HttpResponse("Foreign Key id to name - Conversion Complete!")
    except:
        return HttpResponse("Foreign Key id to name - Conversion Failed!")
@render_to("dcmetadata/test_dajaxice.html")
def test_dajaxice(request):
    return {}

'''------------
Metadata
------------'''

# Display Metadata Entry
@render_to("dcmetadata/metadata_detail.html")
def metadata_detail(request,metadata_id):    
    table_metadata = TableMetadata.objects.get(id=metadata_id)
    metadata_json = table_metadata.metadata
    metadata_json_dict = table_metadata._get_metadata_dict()
    table_tags_dict = metadata_json_dict["table_tags"]
    field_metadata_dict_list = metadata_json_dict["field_metadata"]
    
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.file_name

    return {'source_app_root':SERVER_APP_ROOT,
            'metadata_id':metadata_id,
            'source_data_name':source_data_name,
            'table_tags_dict':table_tags_dict,
            'field_metadata_dict_list':field_metadata_dict_list
            }

# Edit Metadata Entry
@render_to("dcmetadata/metadata_edit.html")
def metadata_edit(request,metadata_id): 
    # Initial vars
    form_has_errors = False # Form Validation Error flag
    is_add_new_metadata = False
    field_metadata_form_list = []
    upload_form = FileUploadForm()
    metadata_json = ""
    
    # Get SourceDataInventory instance
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.file_name
    ## By default, field will inherit table geograhpy, geographic_level, domain, subdomain, and time period
    table_title = source_data.title
    table_geography = source_data.coverage.id
    table_geographic_level = source_data.geography.id
    table_domain = source_data.macro_domain.id
    table_subdomain = source_data.subject_matter.id
    table_year = source_data.year
    table_geometry = source_data.geometry.id
    table_description = source_data.description
    table_data_consideration = source_data.data_consideration
#    table_begin_year = source_data.begin_year
#    table_end_year = source_data.end_year

    # Get TableMetadata instance
    try:
        table_metadata = TableMetadata.objects.get(id=metadata_id)
        metadata_json_dict = table_metadata._get_metadata_dict()
        table_tags_dict = metadata_json_dict["table_tags"]
        field_metadata_dict_list = metadata_json_dict["field_metadata"]
    except:
        table_metadata = TableMetadata(id=metadata_id)
        table_tags_dict = {"title":source_data.title,
                           "geography":source_data.coverage.id,
        				   "geographic_level":source_data.geography.id,
        				   "domain":source_data.macro_domain.id,
        				   "subdomain":source_data.subject_matter.id,
        				   "source":source_data.source.id,
                           "year":source_data.year,
                           "description":source_data.description,
                           "data_consideration":source_data.data_consideration
#        				   "time_period":"%d;%d" % (source_data.begin_year if source_data.begin_year != None else None,source_data.end_year if source_data.end_year != None else None)
        				  }        
        field_metadata_dict_list = []
        metadata_json_dict = {"table_tags":table_tags_dict,
                              "field_metadata":field_metadata_dict_list
                             }
        
    # If field metadata NOT exists
    if source_data.metadata == None and len(field_metadata_dict_list)==0:
        is_add_new_metadata = True
        # Initialize field_metadata_dict structure
        filed_tags_dict = {"title":tabel_title,
                           "geography":table_geography,
                           "geographic_level":table_geographic_level,
                           "domain":table_domain,
                           "subdomain":table_subdomain,
                           "year":table_year,
#                           "time_period":"%d;%d" % (table_begin_year,table_end_year),
                           "visualization_types":"",
                           "geometry":table_geometry,
                           "description":table_description,
                           "data_consideration":table_data_consideration
                          }
        field_metadata_dict_list = [{"field_name":"",
                                     "data_type":"",
                                     "verbose_name":"",
                                     "no_data_value":"",
                                     "tags":filed_tags_dict
                                    }]
        # Initialize field_metadata_form_list
        field_metadata_form_list = [{"field_name":"",
                                     "data_type":"",
                                     "verbose_name":"",
                                     "no_data_value":"",
                                     "geography":table_geography,
                                     "geographic_level":table_geographic_level,
                                     "domain":table_domain,
                                     "subdomain":table_subdomain,
                                     "year":table_year,
#                                     "begin_year":table_begin_year,
#                                     "end_year":table_end_year,
                                     "visualization_types":"",
                                     "geometry":table_geometry                                    
                                    }]
    # Elseif field metadata already exists
    else:
        is_add_new_metadata = False
        # Fill in field_metadata_form_list from field_metadata_dict_list
        for field_metadata_dict in field_metadata_dict_list:
            field_metadata_form = {"field_name":field_metadata_dict["field_name"],
                                   "data_type":field_metadata_dict["data_type"],
                                   "verbose_name":field_metadata_dict["verbose_name"],
                                   "no_data_value":field_metadata_dict["no_data_value"],
                                   "geography":int(field_metadata_dict["tags"]["geography"]) if field_metadata_dict["tags"]["geography"] != None else None,
                                   "geographic_level":int(field_metadata_dict["tags"]["geographic_level"]) if field_metadata_dict["tags"]["geographic_level"] != None else None,
                                   "domain":int(field_metadata_dict["tags"]["domain"]) if field_metadata_dict["tags"]["domain"] != None else None,
                                   "subdomain":int(field_metadata_dict["tags"]["subdomain"]) if field_metadata_dict["tags"]["subdomain"] != None else None,
                                   "year":int(field_metadata_dict["tags"]["year"]) if field_metadata_dict["tags"]["year"] != None else None,
#                                   "begin_year":int(field_metadata_dict["tags"]["time_period"].split(";")[0]) if len(field_metadata_dict["tags"]["time_period"].split(";")) > 1 and field_metadata_dict["tags"]["time_period"].split(";")[0] != "None" else "",
#                                   "end_year":int(field_metadata_dict["tags"]["time_period"].split(";")[1]) if len(field_metadata_dict["tags"]["time_period"].split(";")) > 1 and field_metadata_dict["tags"]["time_period"].split(";")[1] != "None" else "",
                                   "visualization_types":field_metadata_dict["tags"]["visualization_types"],
                                   "geometry":field_metadata_dict["tags"]["geometry"] 
                                   }
            field_metadata_form_list.append(field_metadata_form)
        
    if request.method == 'POST':
        # Read metadata from uploaded file
        ## Notice this "read metadata form uploaded EXCEL workbook" 
        ## will overwrite all the existing field metadata!
        if 'upload_file_submit' in request.POST:
#            if 'upload_file' in request.POST:
            upload_file_name = '%s_header.xls' % source_data.file_name
            file_location = source_data.location
#                header_row = int(request.POST['header_row'])-1
#                file_location = upload_file_location.replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)                
            file_path = os.path.join(file_location,upload_file_name)
            
            # Open xls EXCEL workbook
            xls_workbook = open_workbook(file_path)
            
            xls_sheet = xls_workbook.sheet_by_index(0)
            # Initialize field_metadata_dict_list
            field_metadata_dict_list = []
            # Initialize field_tags_dict
            filed_tags_dict = {"geography":table_geography,
                               "geographic_level":table_geographic_level,
                               "domain":table_domain,
                               "subdomain":table_subdomain,
                               "year":table_year,
#                               "time_period":"%d;%d" % (table_begin_year,table_end_year),
                               "visualization_types":"",
                               "geometry":table_geometry
                              }
            # Initialize field_metadata_form_list
            field_metadata_form_list = []
            # Fill in filed_metadata_dict_list and field_metadata_form_list
            # with the filed_name read from EXCEL file
            xls_headers = []
            xls_dataypes = []
            xls_verbosenames = []
            xls_fills = []
            xls_fills.append(xls_headers)
            xls_fills.append([])
            xls_fills.append(xls_dataypes)
            xls_fills.append(xls_verbosenames)
            for i in [0,2,3]:
                for (index,xls_cell) in enumerate(xls_sheet.row(i)):
                    xls_fills[i].append(xls_cell.value)
            for (i,header) in enumerate(xls_headers):
                if (header != None) and (header != ""):
                    field_metadata_dict_list.append({"field_name":header,
                                                     "data_type":xls_dataypes[i],
                                                     "verbose_name":xls_verbosenames[i],
                                                     "no_data_value":"",
                                                     "tags":filed_tags_dict
                                                    })
                    field_metadata_form_list.append({"field_name":header,
                                                     "data_type":xls_dataypes[i],
                                                     "verbose_name":xls_verbosenames[i],
                                                     "no_data_value":"",
                                                     "geography":table_geography,
                                                     "geographic_level":table_geographic_level,
                                                     "domain":table_domain,
                                                     "subdomain":table_subdomain,
                                                     "year":table_year,
#                                                     "begin_year":table_begin_year,
#                                                     "end_year":table_end_year,
                                                     "visualization_types":"",
                                                     "geometry":table_geometry                                  
                                                     })                      
            
            field_metadata_formset = FieldMetadataFormset(initial=field_metadata_form_list,prefix='metadata_fields_form')
            
            
            return {'file_form':upload_form,
                    'source_app_root':SERVER_APP_ROOT,
                    'is_add_new_metadata':is_add_new_metadata,
                    'source_data_name':source_data_name,
                    'metadata_id':metadata_id,
                    'field_metadata_formset':field_metadata_formset,
                    'form_has_errors':form_has_errors}           
        else:
            field_metadata_formset = FieldMetadataFormset(request.POST,prefix='metadata_fields_form')
            field_metadata_dict_list = []
            # If formset data cleaned
            if field_metadata_formset.is_valid():
                form_data = field_metadata_formset.cleaned_data  
                for index,field in enumerate(form_data):
                    if len(field) > 0:
                        filed_tags_dict = {"geography":field['geography'].id if field['geography'] != None else None,
                                           "geographic_level":field['geographic_level'].id if field['geographic_level'] != None else None,
                                           "domain":field['domain'].id if field['domain'] != None else None,
                                           "subdomain":field['subdomain'].id if field['subdomain'] != None else None,
                                           "year":field['year'] if field['year'] != None else None,
#                                           "time_period":"%s;%s" % (field['begin_year'],field['end_year']) if field['begin_year'] != None and field['end_year'] != None else "",
                                           "visualization_types":field['visualization_types'] if field['visualization_types'] != None else None,
                                           "geometry":field['geometry'].id if field['geometry'] != None else None
                                          }
                        field_metadata_dict = {"field_name":field['field_name'] if field['field_name'] != None else "",
                                               "data_type":field['data_type'] if field['data_type'] != None else "",
                                               "verbose_name":field['verbose_name'] if field['verbose_name'] != None else "",
                                               "no_data_value":field['no_data_value'] if field['no_data_value'] != None else "",
                                               "tags":filed_tags_dict
                                               }
                        field_metadata_dict_list.append(field_metadata_dict)
                    else:
                        # Remove the extra form from formset if the form data is empty
                        field_metadata_formset.forms.pop(index)
                
                metadata_json_dict["field_metadata"] = field_metadata_dict_list                
                metadata_json = json.dumps(metadata_json_dict)
                
                output_metadata = TableMetadata(id=metadata_id,metadata=metadata_json)
                output_metadata.save()
                
                if is_add_new_metadata:
                    source_data.metadata = output_metadata
                    source_data.save()
            # If formset data NOT valid
            else:               
                form_has_errors = True
                if 'save' in request.POST:
                    return {'file_form':upload_form,
                            'source_app_root':SERVER_APP_ROOT,
                            'is_add_new_metadata':is_add_new_metadata,
                            'source_data_name':source_data_name,
                            'metadata_id':metadata_id,
                            'field_metadata_formset':field_metadata_formset,
                            'form_has_errors':form_has_errors}               
            
    else:
        field_metadata_formset = FieldMetadataFormset(initial=field_metadata_form_list,prefix='metadata_fields_form')  

    if 'save' in request.POST:
        # Redirect to Metadata detail page
        return HttpResponseRedirect('%s/dcmetadata/metadata/%s/' % (SERVER_APP_ROOT,metadata_id))
    else:  
        # Return to Metadata edit page
        if len(field_metadata_formset.forms) == 0:
            field_metadata_form_list = [{"field_name":"",
                                         "data_type":"",
                                         "verbose_name":"",
                                         "no_data_value":"",
                                         "geography":table_geography,
                                         "geographic_level":table_geographic_level,
                                         "domain":table_domain,
                                         "subdomain":table_subdomain,
                                         "year":table_year,
#                                         "begin_year":table_begin_year,
#                                         "end_year":table_end_year,
                                         "visualization_types":"",
                                         "geometry":table_geometry                                 
                                        }]
            field_metadata_formset = FieldMetadataFormset(initial=field_metadata_form_list,prefix='metadata_fields_form')           
        return {'file_form':upload_form,
                'source_app_root':SERVER_APP_ROOT,
                'is_add_new_metadata':is_add_new_metadata,
                'source_data_name':source_data_name,
                'metadata_id':metadata_id,
                'field_metadata_formset':field_metadata_formset,
                'form_has_errors':form_has_errors}  

# Delete Metadata Entry
## Metadata entry delete confirm
@render_to("dcmetadata/metadata_delete_confirm.html")
def metadata_delete_confirm(request,metadata_id):
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.file_name

    return {'metadata_id':metadata_id,
            'source_data_name':source_data_name,
            }

## Delete Metadata entry
def metadata_delete(request,metadata_id):
    try:
        metadata = TableMetadata.objects.get(id=metadata_id)
        source_data = SourceDataInventory.objects.get(id=metadata_id)
        source_data.metadata = None
        source_data.save()
    except:
        return HttpResponse("Metadata ID %s dose not exist." % metadata_id)
    
    metadata.delete()
    return HttpResponseRedirect('%s/admin/dcmetadata/sourcedatainventory/' % SERVER_APP_ROOT)