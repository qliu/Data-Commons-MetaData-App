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
                               "time_period":"%d;%d" % (source_data.begin_year if source_data.begin_year != None else 0,source_data.end_year if source_data.end_year != None else 0)
                              }
            
            tree = ElementTree.ElementTree(ElementTree.fromstring(md.metadata))
            root = tree.getroot()
            for field in root[0]:   
                json_field_metadata_tags = {"geography":json_table_tags["geography"],
                                            "geographic_level":json_table_tags["geographic_level"],
                                            "domain":"",
                                            "subdomain":"",
                                            "time_period":"",
                                            "visualization_types":[],
                                            "geometry":""
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
                            
            print json_root_dict
            json_metadata = json.dumps(json_root_dict)
            
            output_metadata = Metadata(id=metadata_id,metadata=md.metadata,metadata_json=json_metadata)
            output_metadata.save()
            
        return HttpResponse("XML to JSON - Conversion complete!")
    except:
        return HttpResponse("XML to JSON - Conversion Failed!")

    
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
    
    table_metadata = TableMetadata.objects.get(id=metadata_id)
    metadata_json = table_metadata.metadata
    metadata_json_dict = table_metadata._get_metadata_dict()
    table_tags_dict = metadata_json_dict["table_tags"]
    field_metadata_dict_list = metadata_json_dict["field_metadata"]
    
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.file_name

    return {'source_app_root':SERVER_APP_ROOT,
            'metadata_id':metadata_id,'metadata_xml':metadata_xml,
            'metadata_fields':metadata_fields,
            'metadata_other':metadata_other,
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
    metadata_xml = ""
    metadata_json = ""
    metadata_list = []
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.file_name
    upload_form = FileUploadForm()
    
    try:
        # If metadata already exists
        metadata =  Metadata.objects.get(id=metadata_id)
        metadata_xml = metadata.metadata
        metadata_list = metadata._get_metadata_dict()
        metadata_fields =  metadata_list[0]
        metadata_other = metadata_list[1]
        metadata_json = metadata._get_metadata_json_dict()
        dataset_tags_dict_list = metadata_json_dict["dataset_tags"]["tags"]
        attribute_tags_dict_list = metadata_json_dict["attribute_tags"]["tags"]
        fields_metadata_dict_list = metadata_json_dict["fields_metadata"]["fields"]        
        
        # If Metadata exists but no fields info
        # Create empty dictionary list for formset initiate
        if len(metadata_fields) == 0:           
            metadata_fields = [{"field_name":"","data_type":"","description":"","tags":""}]
        # If Metadata exists but no other info
        # Create empty dictionary list for formset initiate
        if len(metadata_other) == 0:            
            metadata_other = [{"info_name":"","info_value":""}]
        # If Metadata exists but no dataset tags
        # Create empty dictionary list for formset initiate
        if len(dataset_tags_dict_list) == 0:
            dataset_tags = [{"geography":"","geographic_level":"","domain":"","sub_domain":"","source":"","time_period":""}]
        # If Metadata exists but no attribute tags
        # Create empty dictionary list for formset initiate
        if len(attribute_tags_dict_list) == 0:
            attribute_tags = [{"domain":"","sub_domain":"","time_period":"","visualization_type":"","geometry":""}]
        # If Metadata exists but no fields metadata
        # Create empty dictionary list for formset initiate
        if len(fields_metadata_dict_list) == 0:
            fields_metadata = [{"field_name":"","data_type":"","description":""}]
        
    except:
        # If metadata not exist, Create new instance of Metadata model
        is_add_new_metadata = True
        metadata = Metadata(id=metadata_id)
        # Create empty dictionary list for formset initiate
        metadata_fields = [{"field_name":"","data_type":"","description":"","tags":""}]
        metadata_other = [{"info_name":"","info_value":""}]
        dataset_tags = [{"geography":"","geographic_level":"","domain":"","sub_domain":"","source":"","time_period":""}]
        attribute_tags = [{"domain":"","sub_domain":"","time_period":"","visualization_type":"","geometry":""}]
        fields_metadata = [{"field_name":"","data_type":"","description":""}]
        
    if request.method == 'POST':
        # Read metadata from uploaded file
        if 'upload_file_submit' in request.POST:
            if 'upload_file' in request.POST:
                upload_file_name = request.POST['upload_file']
                upload_file_location = request.POST['upload_file_location']
                header_row = int(request.POST['header_row'])-1
                file_location = upload_file_location.replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)                
                file_path = os.path.join(file_location,upload_file_name)
                
                # Open xls EXCEL workbook
                xls_workbook = open_workbook(file_path)
                
                xls_sheet = xls_workbook.sheet_by_index(0)
                metadata_fields = []
                for xls_cell in xls_sheet.row(header_row):
                    if (xls_cell.value != None) and (xls_cell.value != ""):
                        metadata_fields.append({"field_name":xls_cell.value,"data_type":"","description":"","tags":""})
                        fields_metadata.append({"field_name":xls_cell.value,"data_type":"","description":""})
            
            metadata_fields_formset = MetadataFieldsFormset(initial=metadata_fields,prefix='metadata_fields_form')
            metadata_other_formset = MetadataOtherFormset(initial=metadata_other,prefix='metadata_other_form')
            attribute_tags_formset = MetadataAttributeTagFormset(initial=attribute_tags,prefix='attribute_tags_form')
            fields_metadata_formset = FieldsMetadataFormset(initial=fields_metadata,prefix='fields_metadata_form')
            
            return {'file_form':upload_form,
                    'source_app_root':SERVER_APP_ROOT,
                    'is_add_new_metadata':is_add_new_metadata,
                    'source_data_name':source_data_name,
                    'metadata_id':metadata_id,
                    'metadata_fields_formset':metadata_fields_formset,
                    'metadata_other_formset':metadata_other_formset,
                    'metadata_xml':metadata_xml,
                    'attribute_tags_formset':attribute_tags_formset,
                    'fields_metadata_formset':fields_metadata_formset,
                    'metadata_json':metadata_json,
                    'form_has_errors':form_has_errors,
            }            
        else:
            # Build Element Tree Structure
            et_root =  ElementTree.Element("metadata")
            et_element_fields =  ElementTree.SubElement(et_root,"fields")
            et_element_other =  ElementTree.SubElement(et_root,"other_metadata")
            
            # Build JSON Structure
            json_root_dict = {"dataset_tags":{"tags":""},"attribute_tags":{"tags":""},"fields_metadata":{"fields":""}}
            json_dataset_tags = []
            json_attribute_tags = []
            json_fields_metadata = []
            
            # dataset tags come from "source_data" attributes
            json_dataset_tags_dict = {"geography":source_data.coverage,
                                      "geographic_level":source_data.geography,
                                      "domain":source_data.macro_domain,
                                      "sub_domain":source_data.subject_matter,
                                      "source":source_data.source,
                                      "time_period":"%d;%d" % (source_data.begin_year,source_data.end_year)}
            json_dataset_tags.append(json_dataset_tags_dict)
            
            # Save Fields metadata
            metadata_fields_formset = MetadataFieldsFormset(request.POST,prefix='metadata_fields_form')
            metadata_other_formset = MetadataOtherFormset(request.POST,prefix='metadata_other_form')
            attribute_tags_formset = MetadataAttributeTagFormset(request.POST,prefix='attribute_tags_form')
            fields_metadata_formset = FieldsMetadataFormset(request.POST,prefix='fields_metadata_form')
            
            # If formset data cleaned
            if metadata_fields_formset.is_valid() and metadata_other_formset.is_valid() and attribute_tags_formset.is_valid() and fields_metadata_formset.is_valid():
                fields_data = metadata_fields_formset.cleaned_data          
                for index,field in enumerate(fields_data):
                    if len(field) > 0:
                        et_field = ElementTree.SubElement(et_element_fields,"field_"+str(index+1))
                        et_field_field_name = ElementTree.SubElement(et_field,"field_name")
                        et_field_field_name.text = field['field_name']
                        et_field_data_type = ElementTree.SubElement(et_field,"data_type")
                        et_field_data_type.text =  field['data_type']
                        et_field_description = ElementTree.SubElement(et_field,"description")
                        et_field_description.text = field['description']
                        et_field_tags = ElementTree.SubElement(et_field,"tags")
                        et_field_tags.text = field['tags']
                    else:
                        # Remove the extra form from formset if the form data is empty
                        metadata_fields_formset.forms.pop(index)
                        
                other_data = metadata_other_formset.cleaned_data
                for index,info in enumerate(other_data):
                    if len(info) > 0:
                        et_info = ElementTree.SubElement(et_element_other,"info_"+str(index+1))
                        et_info_name = ElementTree.SubElement(et_info,"info_name")
                        et_info_name.text = info['info_name']
                        et_info_value = ElementTree.SubElement(et_info,"info_value")
                        et_info_value.text = info['info_value']
                    else:
                        # Remove the extra form from formset if the form data is empty
                        metadata_other_formset.forms.pop(index)
                        
                attribute_tags_data = attribute_tags_formset.cleaned_data
                for index,info in enumerate(attribute_tags_data):
                    if len(info) > 0:
                        pass
                        
                metadata.metadata = ElementTree.tostring(et_root)
                metadata.save()
                if is_add_new_metadata:
                    source_data.metadata = metadata
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
                            'metadata_fields_formset':metadata_fields_formset,
                            'metadata_other_formset':metadata_other_formset,
                            'metadata_xml':metadata_xml,
                            'form_has_errors':form_has_errors,
                    }                
            
    else:
        metadata_fields_formset = MetadataFieldsFormset(initial=metadata_fields,prefix='metadata_fields_form')
        metadata_other_formset = MetadataOtherFormset(initial=metadata_other,prefix='metadata_other_form')    

    if 'save' in request.POST:
        # Redirect to Metadata detail page
        return HttpResponseRedirect('%s/dcmetadata/metadata/%s/' % (SERVER_APP_ROOT,metadata_id))
    else:  
        if len(metadata_fields_formset.forms) == 0:
            metadata_fields = [{"field_name":"","data_type":"","description":"","tags":""}]
            metadata_fields_formset = MetadataFieldsFormset(initial=metadata_fields,prefix='metadata_fields_form')
        if len(metadata_other_formset.forms) == 0:
            metadata_other = [{"info_name":"","info_value":""}]
            metadata_other_formset = MetadataOtherFormset(initial=metadata_other,prefix='metadata_other_form')             
        
        # Save data to db and return to Metadata edit page
        return {'file_form':upload_form,
                'source_app_root':SERVER_APP_ROOT,
                'is_add_new_metadata':is_add_new_metadata,
                'source_data_name':source_data_name,
                'metadata_id':metadata_id,
                'metadata_fields_formset':metadata_fields_formset,
                'metadata_other_formset':metadata_other_formset,
                'metadata_xml':metadata_xml,
                'form_has_errors':form_has_errors,
        }

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
        metadata = Metadata.objects.get(id=metadata_id)
        source_data = SourceDataInventory.objects.get(id=metadata_id)
        source_data.metadata = None
        source_data.save()
    except:
        return HttpResponse("Metadata ID %s dose not exist." % metadata_id)
    
    metadata.delete()
    return HttpResponseRedirect('%s/admin/dcmetadata/sourcedatainventory/' % SERVER_APP_ROOT)