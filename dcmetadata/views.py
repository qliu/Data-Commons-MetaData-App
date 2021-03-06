from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import models
from django.db.models.loading import get_model
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm

# Import from general utilities
from util import *

from dcmetadata.models import *
from dcmetadata.forms import *

'''-----------------------
TEST functions
-----------------------'''
# AJAX Admin get Subject Matter on selected Macro Domain
def ajax_get_subjectmatter(request):
    if request.is_ajax() and request.method == 'POST':
        macrodomain_id = int(request.POST.get('macrodomain',''))
        subjectmatters = SubjectMatter.objects.filter(macrodomain=macrodomain_id)
    return HttpResponse(subjectmatters,mimetype="text/plain")

# Test
def test(request):
    q = 'mdb'
    test_format = Format.objects.extra(
        where=['ext_tsv @@ plainto_tsquery(%s)'],params=[q])

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


# Convert tag name to tag id for "tags" key in dataset metadata
def tagsname2id(request):
    metadata_json = ""
    try:
        dataset_metadata = DatasetMetadata.objects.all()
        for dm in dataset_metadata:
            metadata_id = dm.id
            dataset = Dataset.objects.get(id=metadata_id)
            metadata_json_dict = dm._get_metadata_dict()
            metadata_json_dict["tags"] = map(int,dataset._get_str_tags().split(","))
            metadata_json = json.dumps(metadata_json_dict)
            output_metadata = DatasetMetadata(id=metadata_id,metadata=metadata_json)
            output_metadata.save()
        return HttpResponse("\"Tags\" Key name to id - Conversion complete!")
    except Exception as e:
        return HttpResponse("\"Tags\" Key name to id - Conversion Failed!")

# Add and Initialize "update_date" key in dataset metadata
def addupdatedate(request):
    metadata_json = ""
    try:
        dataset_metadata = DatasetMetadata.objects.all()
        for dm in dataset_metadata:
            metadata_id = dm.id
            metadata_json_dict = dm._get_metadata_dict()
            metadata_json_dict["update_date"] = datetime.date.today().strftime("%Y-%m-%d")
            metadata_json = json.dumps(metadata_json_dict)
            output_metadata = DatasetMetadata(id=metadata_id,metadata=metadata_json)
            output_metadata.save()
        return HttpResponse("Add and Initialzie \"update_date\" Key - Succeed!")
    except Exception as e:
        return HttpResponse("Add and Initialzie \"update_date\" Key - Failed!")
            

'''-----------------------
Import data from metadata
-----------------------'''
# Import Dataset from Dataset Metadata
## If dataset already existed, update it with metadata,
## Else create new dataset.
def import_dataset(request):
    try:
        dataset_metadata_all = DatasetMetadata.objects.all()
        for dm in dataset_metadata_all:
            dm_dict = dm._get_metadata_dict()
            # get_or_create return a tuple of (model,bool)
            ## where model is the object, bool telss you whether it had to be created or not
            return_dataset = Dataset.objects.get_or_create(id=dm.id)
            dataset = return_dataset[0]
            dataset.nid = dm_dict["nid"]
            dataset.name = dm_dict["name"]
            dataset.large_dataset = dm_dict["large_dataset"]
            dataset.metadata = dm
            for table_id in dm_dict["tables"]:
                table = SourceDataInventory.objects.get(id=table_id)
                dataset.tables.add(table)
            for tag_id in dm_dict["tags"]:
                # If tag NOT existed, create new tag
                return_tag = Tag.objects.get_or_create(id=tag_id)
                tag = return_tag[0]
                dataset.tags.add(tag)
            dataset.save()
        return HttpResponse("Import Dataset from Dataset Metadata - Dataset Successfully Imported!")
    except:
        return HttpResponse("Import Dataset from Dataset Metadata - Import Failed!")


# Import Source Data from Data Table Metadata
def import_sourcedata(request):
#    try:
    table_metadata_all = TableMetadata.objects.all()
    for tm in table_metadata_all:
        tm_dict = tm._get_metadata_dict()
        table_dict = tm_dict["table_tags"]
        return_sourcedata = SourceDataInventory.objects.get_or_create(id=tm.id)
        sourcedata = return_sourcedata[0]
        if return_sourcedata[1]:
            try:
                return_datatable = DataTable.objects.get_or_create(id=tm.id)
                datatable = return_datatable[0]
                if return_datatable[1]:
                    datatable.name = "New Data Table Imported!"
                    datatable.save()
            except:
                pass
            
        sourcedata.title = table_dict["title"]
        sourcedata.year = table_dict["year"]
        sourcedata.source_website = table_dict["source_website"]
        sourcedata.description = table_dict["description"]
        sourcedata.data_consideration = table_dict["data_consideration"]
        sourcedata.process_notes = "This source data was imported from table metadata."
        macro_domain = MacroDomain.objects.get_or_create(id=table_dict["domain"])[0]
        if MacroDomain.objects.get_or_create(id=table_dict["domain"])[1]:
            macro_domain.name = "New Domain Imported!"
            macro_domain.save()
        sourcedata.macro_domain = macro_domain
        subject_matter = SubjectMatter.objects.get_or_create(id=table_dict["subdomain"])[0]
        if SubjectMatter.objects.get_or_create(id=table_dict["subdomain"])[1]:
            subject_matter.name = "New Subdomain Imported!"
            subject_domain.save()
        sourcedata.subject_matter = subject_matter
        geography = Geography.objects.get_or_create(id=table_dict["geographic_level"])[0]
        if Geography.objects.get_or_create(id=table_dict["geographic_level"])[1]:
            geography.name = "New Geographic Level Imported!"
            geography.save()
        sourcedata.geography = geography
        coverage = Coverage.objects.get_or_create(id=table_dict["geography"])[0]
        if Coverage.objects.get_or_create(id=table_dict["geography"])[1]:
            coverage.name = "New Geography Imported!"
            coverage.save()
        sourcedata.coverage = coverage
        source = Source.objects.get_or_create(id=table_dict["source"])[0]
        if Source.objects.get_or_create(id=table_dict["source"])[1]:
            source.name = "New Source Imported!"
            source.save()
        sourcedata.source = source
        geometry = SpatialTable.objects.get_or_create(id=table_dict["geometry"])[0]
        if SpatialTable.objects.get_or_create(id=table_dict["geometry"])[1]:
            geometry.name = "New Spatial Table Imported!"
            geometry.save()
        sourcedata.geometry = geometry
        
        sourcedata.metadata = tm
        sourcedata.save()
        
    return HttpResponse("Import Source Data from Table Metadata - Source Data Successfully Imported!")
#    except:
#        return HttpResponse("Import Source Data from Table Metadata - Import Failed!")

# Help Document page of PyQt4 GUI tool for uploading Excel table to database
@render_to("dcmetadata/db_upload_help_doc.html")
def db_upload_help_doc(request):
    return {}

'''-----------------------
User functions
-----------------------'''
# Login Page
@render_to("admin/login.html")
def user_login(request):
    title = "Login"
    if request.method == 'POST':
        authform = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('%s/dcmetadata/home/' % APP_SERVER_URL)
        else:
            error_msg = "Incorrect username or password."
            return {'error_msg':error_msg,'form':authform,'title':title}
    else:
        authform = AuthenticationForm()
        return {'form':authform,'title':title}
    
# Register
@render_to("dcmetadata/register.html")
def register(request):
    if request.method == 'POST':
        signup_form = UserCreationForm(request.POST)
        if signup_form.is_valid():
            new_user = signup_form.save()
            user = authenticate(username=signup_form.cleaned_data["username"], password=signup_form.cleaned_data["password2"])
            login(request, user)
            return HttpResponseRedirect('%s/dcmetadata/user/profile/' % APP_SERVER_URL)
        else:
            error_msg = "Please check your register information."
            return {'title':"Sign up",'error_msg':error_msg,'signup_form':signup_form}
    else:
        signup_form = UserCreationForm()
    return {'title':"Sign up",'signup_form':signup_form}


# User Profile
@login_required
@render_to("dcmetadata/user_profile.html")
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        user_profile_form = UserProfileForm(instance=user)
    elif request.method == 'POST':
        user_profile_form = UserProfileForm(data=request.POST, instance=user)
        if user_profile_form.is_valid():
            user_profile_form.save()
            messages.info(request, "User profile was changed successfully.")
            if 'save' in request.POST:
                return HttpResponseRedirect('%s/dcmetadata/home/' % APP_SERVER_URL)
        else:
            messages.error(request, "Please correct the errors below.")
    return {'user_name':user.username,'user_profile_form':user_profile_form}

# User Change Password
@login_required
@render_to("dcmetadata/user_password.html")
def user_change_password(request):
    user = request.user
    if request.method == 'GET':
        user_password_form = PasswordChangeForm(user)
    elif request.method == 'POST':
        user_password_form = PasswordChangeForm(user,request.POST)
        if user_password_form.is_valid():
            user_password_form.save()
            messages.info(request, "User password was changed successfully.")
            return HttpResponseRedirect('%s/dcmetadata/user/profile/' % APP_SERVER_URL)
        else:
            messages.error(request, "Please correct the errors below.")
    return {'user_name':user.username,'user_password_form':user_password_form}


'''-----------------------
Database functions
-----------------------'''
# Generate CSVs, Shapefiles, and Metadata(CSV), and Wrap for Download as Zip archive
@login_required
def down_as_zip(request,sourcedata_ids):
    # Initialize DB connection
    dbcon_dc = psycopg2.connect(database = DL_DATABASE["DATABASE"],
                                user = DL_DATABASE["USER"],
                                host = DL_DATABASE["HOST"],
                                port = DL_DATABASE["PORT"],
                                password = DL_DATABASE["PASSWORD"])
    
    output_files = []
    
    for sourcedata_id in sourcedata_ids:
        # Get source data
        source_data = SourceDataInventory.objects.get(id=sourcedata_id)
        table_name = source_data.file_name
        # Get source data metadata
        table_metadata = TableMetadata.objects.get(id=sourcedata_id)
        metadata_json_dict = table_metadata._get_metadata_dict()
        fields = metadata_json_dict["field_metadata"]
        header = []
        dl_metadata = [("Field Name","Verbose Name","Data Type","No Data Value")]
        for field in fields:
            header.append(field["field_name"])
            dl_metadata.append((field["field_name"],field["verbose_name"],field["data_type"],field["no_data_value"]))
        # Write Metadata to CSV
        output_metadata = StringIO.StringIO()
        writer = csv.writer(output_metadata)
        for row in dl_metadata:
            writer.writerow(row)        
        if source_data.macro_domain.name == 'Geography':
            # Download shapefile
            file_location = source_data.location.replace(SOURCE_DATA_ROOT_PATH_LOCAL,SOURCE_DATA_ROOT_PATH_ORIGIN) # <- Localhost Use This Line
#            file_location = source_data.location # <- Server Use This Line
            shp_files = []
            for f in os.listdir(file_location):
                f_name,f_ext = os.path.splitext(f)
                if (f_ext[1:] in SHAPEFILE_EXTENSION and f_name == source_data.file_name) or (f_ext == ".xml" and f_name == "%.shp" % source_data.file_name):
                    shp_files.append(f)
            
            output_file = (table_name,output_metadata,shp_files,"shp")            
        else:
            # Download CSV from DB
            ## Create DB table
            try:
                cur_dc = dbcon_dc.cursor()
                ## Check if talbe exists
                exesql = "SELECT * FROM %s" % table_name
                cur_dc.execute(exesql)
                source_table = cur_dc.fetchall()
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                error_type = exc_type.__name__
                error_info = exc_obj
                if str(error_info).find('relation "%s" does not exist' % table_name) > -1:
                    user_error_msg = 'Table "<b>%s</b>" does not exist in the database.' % table_name
                else:
                    user_error_msg = "- Debug Mode -"
                error_msg = "<span style='color:red'><b>ERROR!</b></span><br/><br/><b>%s</b><br/><br/><br/><b>%s</b> : %s" % (user_error_msg,error_type,error_info)
                return HttpResponse(error_msg)
        
            # Write Table to CSV
            output_table = StringIO.StringIO()
            writer = csv.writer(output_table)
            writer.writerow(header)
            for row in source_table:
                writer.writerow(row)
            output_file = (table_name,output_metadata,output_table,"table")
            
        output_files.append(output_file)
            
    # Zip CSVs up
    zip_name = "SourceData_%s" % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    temp = tempfile.TemporaryFile()
    buffer = zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED)
    for of in output_files:
        if of[3] == "shp":
        ## Shape file
            buffer.writestr("%s_shp/%s_metadata.csv" % (of[0],of[0]), of[1].getvalue())
            for shp_f in of[2]:
                full_path = "%s\%s" % (file_location,shp_f)
                zip_path = "%s_shp/%s" % (of[0],shp_f)
                buffer.write(full_path,zip_path)
        elif of[3] == "table":
        ## Non-geo table
            buffer.writestr("%s_metadata.csv" % of[0], of[1].getvalue())
            buffer.writestr("%s.csv" % of[0], of[2].getvalue())
    buffer.close()
    wrapper = FileWrapper(temp)  
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = "attachment; filename=%s.zip" % zip_name
    response['Content-Legnth'] = temp.tell()
    temp.seek(0)
    
    return response

# Download source data
@login_required
def download_sourcedata(request,sourcedata_id):
    sourcedata_ids = [sourcedata_id]
    response = down_as_zip(request,sourcedata_ids)
    return response

# Show Instructions of Adding Query Layer in ArcGIS
@login_required
@render_to("dcmetadata/instruction_add_querylayer.html")
def instruction_add_querylayer(request,sourcedata_id):
    source_data = SourceDataInventory.objects.get(id=sourcedata_id)
    table_title = source_data.title
    table_name = source_data.file_name
    query_txt = "SELECT * FROM %s.%s.%s" % (DL_DATABASE["DATABASE"],DL_DATABASE["SCHEMA"],table_name)

    return {"sourcedata_id":sourcedata_id,
            "table_title":table_title,
            "query_txt":query_txt,
            }

'''-----------------------
Home Page
-----------------------'''
# Home page
@login_required
@render_to("dcmetadata/home.html")
def home(request):
    return {}

'''------------
Dataset
------------'''
# Display Dataset Metadata
@login_required
@render_to("dcmetadata/dataset_metadata_detail.html")
def dataset_metadata_detail(request,dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)
    tables = dataset.tables.all()
    dataset_metadata = get_object_or_404(DatasetMetadata, id=dataset_id)
    dataset_metadata_dict = dataset_metadata._get_metadata_dict()
    user = request.user
    has_change_permission = HasPermission(user,'dcmetadata','change','tablemetadata')
    has_delete_permission = HasPermission(user,'dcmetadata','delete','tablemetadata')
    
    # Construct a dictionary to hold table fields in the dataset
    dataset_table_metadata_fields = {}
    for table in tables:
        dataset_table_metadata_fields[table.id] = {}
    for table in tables:
        table_metadata = TableMetadata.objects.get(id=table.id)
        field_metadata_dict_list = table_metadata._get_metadata_dict()["field_metadata"]
        for table_field in field_metadata_dict_list:
            dataset_table_metadata_fields[table.id][table_field["field_name"].lower()] = [table_field["verbose_name"],table_field["data_type"]]
    
    # Retrieve field metadata
    dataset_fields = dataset_metadata_dict["fields"]
    dataset_fields_metadata = []
    for dataset_field in dataset_fields:
        dataset_field_str_list = dataset_field.split(".")
        table_id = int(dataset_field_str_list[0])
        field_name = dataset_field_str_list[1]
        field_metadata = {"field_name":field_name,
                          "verbose_name":dataset_table_metadata_fields[table_id][field_name][0],
                          "data_type":dataset_table_metadata_fields[table_id][field_name][1]
                         }
        dataset_fields_metadata.append(field_metadata)
    
    return {'dataset_id':dataset_id,
            'dataset':dataset,
            'tables':tables,
            'dataset_metadata':dataset_metadata_dict,
            'field_metadata_dict_list':dataset_fields_metadata,
            'has_change_permission':has_change_permission,
            'has_delete_permission':has_delete_permission,
            }

# Add Dataset Metadata
@login_required
@render_to("dcmetadata/dataset_metadata_edit.html")
def dataset_metadata_edit(request,dataset_id):
    # Initial vars
    is_add_new_metadata = False
    tables = [] # list of dict storing table_id,table_name,table_fields for forms
    user = request.user
    has_delete_permission = HasPermission(user,'dcmetadata','delete','tablemetadata')
    
    # Initial Dataset metadata
    dataset = get_object_or_404(Dataset, id=dataset_id)  
    dataset_metadata = get_object_or_404(DatasetMetadata,id=dataset_id)
    ## If dataset metadata NOT exsit, initial dataset metadata dictionary with
    ##  dataset attributes.
    if dataset_metadata.metadata == "{}":
        is_add_new_metadata =  True
        dataset_dict = {"nid":dataset.nid if dataset.nid else "",
                        "name":dataset.name,
                        "tables":map(int,dataset._get_str_tables().split(",")),
                        "fields":[],
                        "display_name":"",
                        "pkey":[],
                        "fkeys":[],
                        "gkey":[],
                        "tags":map(int,dataset._get_str_tags().split(",")),
                        "large_dataset":dataset.large_dataset,
                        "update_date":dataset.update_date.strftime("%Y-%m-%d")
                        }
    ## If dataset metadata esixts, read the dictionary from database.
    else:
        dataset_dict = dataset_metadata._get_metadata_dict()
        ## Check if dataset_dict has key "fields", since some of the datasets
        ##  that contains only one table may not have metadata key "fields".
        if not dataset_dict.has_key("fields") and len(dataset_dict["tables"]) == 1:
            dataset_dict["fields"] = []
    
    # Read fields metadata for each table in the dataset
    for index,table_id in enumerate(dataset_dict["tables"]):
        table = get_object_or_404(TableMetadata,id=table_id)
        table_metadata = table._get_metadata_dict()
        ## Get spatial table id
        if index == 0:
            spatial_table_id = table_metadata["table_tags"]["geometry"]
        fields = []
        for field in table_metadata["field_metadata"]:
            fields.append({"field_name":field["field_name"].lower(),
                           "verbose_name":field["verbose_name"]
                          })
        tables.append({
                        "table_id":table_id,
                        "table_name":table_metadata["table_tags"]["title"],
                        "table_fields":fields
                      })    
    # Preparing initial values for Forms and Formset
    ## Number of forms in formset is decided by the number of tables in dataset
    num_tables = len(tables)
    ## Preparing choice values for Form ChoiceField/MultipleChoiceField
    field_choice_list_main = []
    field_choice_list_full = []
    for index,t in enumerate(tables):
        table_list_separator = "* Table%d: %s" % (t["table_id"],t["table_name"])
        field_choice_list_full.append((None,table_list_separator))
        if index == 0:
            field_choice_list_main.append((None,table_list_separator))
        for f in t["table_fields"]:
            table_field_return_value = "%d.%s" % (t["table_id"],f["field_name"])
            table_field_display_value = "Table%d.[%s]" % (t["table_id"],f["verbose_name"])
            field_choice_list_full.append((table_field_return_value,table_field_display_value))
            if index == 0:
                 field_choice_list_main.append((table_field_return_value,table_field_display_value))
                
    # Read fields metadata for spaital table
    spatial_table = get_object_or_404(TableMetadata,id=spatial_table_id)
    spatial_table_metadata = spatial_table._get_metadata_dict()
    fields = []
    for field in spatial_table_metadata["field_metadata"]:
        fields.append({"field_name":field["field_name"],
                       "verbose_name":field["verbose_name"]
                       })
    spatial_table_fields = {
                            "table_id":spatial_table_id,
                            "table_name":spatial_table_metadata["table_tags"]["title"],
                            "table_fields":fields
                            }
    # Preparing choice values for spatial table
    field_choice_list_spatial = []
    table_list_separator = "== Spatial Table ID %d: %s ==" % (spatial_table_fields["table_id"],spatial_table_fields["table_name"])
    field_choice_list_spatial.append((None,table_list_separator))
    for f in spatial_table_fields["table_fields"]:
        table_field_return_value = "%d.%s" % (spatial_table_fields["table_id"],f["field_name"])
        field_choice_list_spatial.append((table_field_return_value,f["verbose_name"]))        
    
    # Handling Forms
    if request.method == 'POST':
        dataset_metadata_form = DatasetMetadataForm(request.POST)
        dataset_metadata_fkey_formset = DatasetMetadataFKeyFormSet(request.POST)
        
        ## Initializing DatasetMetadataForm list choices
        dataset_metadata_form.fields["fields"].choices = field_choice_list_full
        dataset_metadata_form.fields["display_name"].choices = field_choice_list_full
        dataset_metadata_form.fields["pkey"].choices = field_choice_list_full
        dataset_metadata_form.fields["gkey_main"].choices = field_choice_list_main
        dataset_metadata_form.fields["gkey_spatial"].choices = field_choice_list_spatial
        ## Initializing DatasetMetadataFKeyFormSet list choices
        for index,dataset_metadata_fkey_form in enumerate(dataset_metadata_fkey_formset):
            dataset_metadata_fkey_form.fields["foreign_key"].label = "FKey %d: Foreign Key" % (index+1)
            dataset_metadata_fkey_form.fields["foreign_key"].choices = field_choice_list_full
            dataset_metadata_fkey_form.fields["reference_key"].label = "FKey %d: Reference Key" % (index+1)
            dataset_metadata_fkey_form.fields["reference_key"].choices = field_choice_list_full
                
        # If data cleaned
        if dataset_metadata_form.is_valid() & dataset_metadata_fkey_formset.is_valid():
            dataset_metadata_form_cleaned_data = dataset_metadata_form.cleaned_data
            dataset_metadata_fkey_formset_cleaned_data = dataset_metadata_fkey_formset.cleaned_data
            
            dataset_dict['fields'] = dataset_metadata_form_cleaned_data["fields"]
            dataset_dict['display_name'] = dataset_metadata_form_cleaned_data["display_name"]
            dataset_dict['pkey'] = dataset_metadata_form_cleaned_data["pkey"]
            dataset_dict['gkey'] = [dataset_metadata_form_cleaned_data["gkey_main"],dataset_metadata_form_cleaned_data["gkey_spatial"]]
            fkeys = []
            for fk in dataset_metadata_fkey_formset_cleaned_data:
                fkeys.append([fk["foreign_key"],fk["reference_key"]])
            dataset_dict['fkeys'] = fkeys
            
            metadata_json = json.dumps(dataset_dict)
            dataset_metadata.metadata = metadata_json
            dataset_metadata.save()
            
            if is_add_new_metadata:
                dataset.metadata = dataset_metadata
                dataset.save()
                messages.info(request, "Dataset metadata was added successfully.")
            else:
                messages.info(request, "Dataset metadata was changed successfully.")
            
        else:
            messages.error(request, "Please correct the errors below.")
            return {'dataset_id':dataset_id,
                    'dataset_name':dataset_dict["name"],
                    'tables':tables,
                    'dataset_metadata_form':dataset_metadata_form,
                    'dataset_metadata_fkey_formset':dataset_metadata_fkey_formset,
                    'is_add_new_metadata':is_add_new_metadata,
                    'has_delete_permission':has_delete_permission,
                    }
    else:
        ## Initializing DatasetMetadataFKeyFormSet
        initial_formset_data = {
                                'form-TOTAL_FORMS': u'%d' % (num_tables-1),
                                'form-INITIAL_FORMS': u'0',
                                'form-MAX_NUM_FORMS': u'%d' % (num_tables-1),
                                }
        ## If dataset metadata NOT exist, initialize Form and Formset with NONE value
        if is_add_new_metadata:
            dataset_metadata_form = DatasetMetadataForm()
            dataset_metadata_fkey_formset = DatasetMetadataFKeyFormSet(initial_formset_data,initial=None)
        ## If dataset metadata exists, initialize Form and Formset with dict value
        else:
            dataset_metadata_form_initial_dict = {
                'fields':dataset_dict["fields"],
                'display_name':dataset_dict["display_name"],
                'pkey':dataset_dict["pkey"],
                'gkey_main':dataset_dict["gkey"][0] if len(dataset_dict["gkey"]) > 0 else None,
                'gkey_spatial':dataset_dict["gkey"][1] if len(dataset_dict["gkey"]) > 0 else None
            }
            dataset_metadata_form = DatasetMetadataForm(dataset_metadata_form_initial_dict)
            ### Snippet -> Using Django Admin FilteredSelectMultiple widget outside admin site
            dataset_metadata_form.fields['fields'].widget.attrs['class'] = 'filtered'
            dataset_metadata_form.fields['pkey'].widget.attrs['class'] = 'filtered'
            ### <- Snippet
            ## If FKeys exists:
            if len(dataset_dict["fkeys"]) > 0:
                dataset_metadata_fkey_formset_initial_list = []
                for fk in dataset_dict["fkeys"]:
                    dataset_metadata_fkey_formset_initial_list.append(
                        {'foreign_key':fk[0],
                         'reference_key':fk[1]
                        })
                dataset_metadata_fkey_formset = DatasetMetadataFKeyFormSet(initial=dataset_metadata_fkey_formset_initial_list)
            else:
                dataset_metadata_fkey_formset = DatasetMetadataFKeyFormSet(initial_formset_data,initial=None)
            
        ## Initializing DatasetMetadataForm list choices
        dataset_metadata_form.fields["fields"].choices = field_choice_list_full
        dataset_metadata_form.fields["display_name"].choices = field_choice_list_full
        dataset_metadata_form.fields["pkey"].choices = field_choice_list_full
        dataset_metadata_form.fields["gkey_main"].choices = field_choice_list_main
        dataset_metadata_form.fields["gkey_spatial"].choices = field_choice_list_spatial
        ## Initializing DatasetMetadataFKeyFormSet list choices
        for index,dataset_metadata_fkey_form in enumerate(dataset_metadata_fkey_formset):
            dataset_metadata_fkey_form.fields["foreign_key"].label = "FKey %d: Foreign Key" % (index+1)
            dataset_metadata_fkey_form.fields["foreign_key"].choices = field_choice_list_full
            dataset_metadata_fkey_form.fields["reference_key"].label = "FKey %d: Reference Key" % (index+1)
            dataset_metadata_fkey_form.fields["reference_key"].choices = field_choice_list_full

    if 'save' in request.POST:
        # Redirect to Metadata detail page
        return HttpResponseRedirect('%s/admin/dcmetadata/dataset/%s/' % (SERVER_APP_ROOT,dataset_id))
    else:
        return {'dataset_id':dataset_id,
                'dataset_name':dataset_dict["name"],
                'tables':tables,
                'dataset_metadata_form':dataset_metadata_form,
                'dataset_metadata_fkey_formset':dataset_metadata_fkey_formset,
                'is_add_new_metadata':is_add_new_metadata,
                'has_delete_permission':has_delete_permission,
                }
                
# Delete Dataset Metadata Entry
## Dataset Metadata entry delete confirm
@login_required
@render_to("dcmetadata/dataset_metadata_delete_confirm.html")
def dataset_metadata_delete_confirm(request,dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)
    dataset_name = dataset.name

    return {'dataset_id':dataset_id,
            'dataset_name':dataset_name
            }

## Delete Dataset Metadata entry
@login_required
def dataset_metadata_delete(request,dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)
    dataset_metadata = get_object_or_404(DatasetMetadata, id=dataset_id)
    dataset_metadata.metadata = "{}"
    dataset.metadata = None
    dataset.save()
    dataset_metadata.save()
    return HttpResponseRedirect('%s/admin/dcmetadata/dataset/' % SERVER_APP_ROOT)


'''------------
Metadata
------------'''

# Display Metadata Entry
@login_required
@render_to("dcmetadata/metadata_detail.html")
def metadata_detail(request,metadata_id):    
    table_metadata = TableMetadata.objects.get(id=metadata_id)
    metadata_json_dict = table_metadata._get_metadata_dict()
    table_tags_dict = metadata_json_dict["table_tags"]
    field_metadata_dict_list = metadata_json_dict["field_metadata"]    
    source_data = SourceDataInventory.objects.get(id=metadata_id)
#    source_data_name = source_data.title
    datasets = source_data.dataset_set.all()
    list_datasets = []
    for dataset in datasets:
        ds = {"name":dataset.name,
              "id":dataset.id,   
             }
        list_datasets.append(ds)
    user = request.user
    has_change_permission = HasPermission(user,'dcmetadata','change','tablemetadata')
    has_delete_permission = HasPermission(user,'dcmetadata','delete','tablemetadata')

    return {
            'metadata_id':metadata_id,
#            'source_data_name':source_data_name,
            'source_data':source_data,
            'datasets':list_datasets,
            'table_tags_dict':table_tags_dict,
            'field_metadata_dict_list':field_metadata_dict_list,
            'has_change_permission':has_change_permission,
            'has_delete_permission':has_delete_permission,
            }

# Edit Metadata Entry
@login_required
@render_to("dcmetadata/metadata_edit.html")
def metadata_edit(request,metadata_id): 
    # Initial vars
    is_add_new_metadata = False
    is_geography_table = False
    field_metadata_form_list = []
    upload_form = FileUploadForm()
    metadata_json = ""
    user = request.user
    has_delete_permission = HasPermission(user,'dcmetadata','delete','tablemetadata')
    
    # Get SourceDataInventory instance
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.title
    ## By default, field will inherit table geograhpy, geographic_level, domain, subdomain, year, and geometry
    table_geography = source_data.coverage.id
    table_geographic_level = source_data.geography.id
    table_domain = source_data.macro_domain.id
    table_subdomain = source_data.subject_matter.id
    table_year = source_data.year
    table_geometry = source_data.geometry.id

    # If is spatial table, disable upload metadata from header file
    if source_data.macro_domain.name == "Geography":
        is_geography_table = True

    # Get TableMetadata instance
    try:
        table_metadata = TableMetadata.objects.get(id=metadata_id)
        metadata_json_dict = table_metadata._get_metadata_dict()
        table_tags_dict = metadata_json_dict["table_tags"]
        field_metadata_dict_list = metadata_json_dict["field_metadata"]
    except:
        ## If table metadata not exists
        table_metadata = TableMetadata(id=metadata_id)
        table_tags_dict = {"title":source_data.title,
                           "geography":source_data.coverage.id,
        				   "geographic_level":source_data.geography.id,
        				   "domain":source_data.macro_domain.id,
        				   "subdomain":source_data.subject_matter.id,
        				   "source":source_data.source.id,
                           "source_website":source_data.source_website,
                           "year":source_data.year,
                           "description":source_data.description,
                           "data_consideration":source_data.data_consideration
        				  }        
        field_metadata_dict_list = []
        metadata_json_dict = {"table_tags":table_tags_dict,
                              "field_metadata":field_metadata_dict_list
                             }
        
    # If field metadata NOT exists
    if source_data.metadata == None and len(field_metadata_dict_list)==0:
        is_add_new_metadata = True
        # Initialize field_metadata_dict structure
        field_tags_dict = {
                           "geography":table_geography,
                           "geographic_level":table_geographic_level,
                           "domain":table_domain,
                           "subdomain":table_subdomain,
                           "year":table_year,
                           "visualization_types":[],
                           "geometry":table_geometry,
                          }
        field_metadata_dict_list = [{"field_name":"",
                                     "data_type":"",
                                     "verbose_name":"",
                                     "no_data_value":"",
                                     "tags":field_tags_dict
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
                                     "visualization_types":[],
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
                                   "visualization_types":field_metadata_dict["tags"]["visualization_types"],
                                   "geometry":field_metadata_dict["tags"]["geometry"] 
                                   }
            field_metadata_form_list.append(field_metadata_form)
        
    if request.method == 'POST':
        # Read metadata from uploaded file
        ## Notice this "read metadata form uploaded EXCEL workbook" 
        ##  will overwrite all the existing field metadata!
        if 'upload_file_submit' in request.POST:
            upload_file_name = '%s_header.xls' % source_data.file_name
            file_location = source_data.location               
            file_path = os.path.join(file_location,upload_file_name)
            if not os.path.exists(file_path):
                upload_file_name = '%s_header.xlsx' % source_data.file_name              
                file_path = os.path.join(file_location,upload_file_name)
            
            # Open xls EXCEL workbook
            xls_workbook = open_workbook(file_path)
            xls_sheet = xls_workbook.sheet_by_index(0)
            # Initialize field_metadata_dict_list
            field_metadata_dict_list = []
            # Initialize field_tags_dict
            field_tags_dict = {"geography":table_geography,
                               "geographic_level":table_geographic_level,
                               "domain":table_domain,
                               "subdomain":table_subdomain,
                               "year":table_year,
                               "visualization_types":[],
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
                                                     "tags":field_tags_dict
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
                                                     "visualization_types":[],
                                                     "geometry":table_geometry                                  
                                                     })                      
            
            field_metadata_formset = FieldMetadataFormset(initial=field_metadata_form_list,prefix='metadata_fields_form')
            
            
            return {'file_form':upload_form,
                    'is_add_new_metadata':is_add_new_metadata,
                    'is_geography_table':is_geography_table,
                    'source_data_name':source_data_name,
                    'metadata_id':metadata_id,
                    'field_metadata_formset':field_metadata_formset,
                    'has_delete_permission':has_delete_permission}           
        else:
            field_metadata_formset = FieldMetadataFormset(request.POST,prefix='metadata_fields_form')
            field_metadata_dict_list = []
            # If formset data cleaned
            if field_metadata_formset.is_valid():
                form_data = field_metadata_formset.cleaned_data 
                for index,field in enumerate(form_data):
                    visualization_types = []
                    for v_types in field['visualization_types']:
                        visualization_types.append(v_types.id)
                    if len(field) > 0:
                        field_tags_dict = {"geography":field['geography'].id if field['geography'] != None else None,
                                           "geographic_level":field['geographic_level'].id if field['geographic_level'] != None else None,
                                           "domain":field['domain'].id if field['domain'] != None else None,
                                           "subdomain":field['subdomain'].id if field['subdomain'] != None else None,
                                           "year":field['year'] if field['year'] != None else None,
                                           "visualization_types":visualization_types if field['visualization_types'] != None else None,
                                           "geometry":field['geometry'].id if field['geometry'] != None else None
                                          }
                        field_metadata_dict = {"field_name":field['field_name'] if field['field_name'] != None else "",
                                               "data_type":field['data_type'] if field['data_type'] != None else "",
                                               "verbose_name":field['verbose_name'] if field['verbose_name'] != None else "",
                                               "no_data_value":field['no_data_value'] if field['no_data_value'] != None else "",
                                               "tags":field_tags_dict
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
                    messages.info(request, "Metadata was added successfully.")
                else:
                    messages.info(request, "Metadata was changed successfully.")
            # If formset data NOT valid
            else:               
                messages.error(request, "Please correct the errors below.")
                if 'save' in request.POST:
                    return {'file_form':upload_form,
                            'is_add_new_metadata':is_add_new_metadata,
                            'is_geography_table':is_geography_table,
                            'source_data_name':source_data_name,
                            'metadata_id':metadata_id,
                            'field_metadata_formset':field_metadata_formset,
                            'has_delete_permission':has_delete_permission}               
            
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
                                         "visualization_types":[],
                                         "geometry":table_geometry                                 
                                        }]
            field_metadata_formset = FieldMetadataFormset(initial=field_metadata_form_list,prefix='metadata_fields_form')           
        return {'file_form':upload_form,
                'is_add_new_metadata':is_add_new_metadata,
                'is_geography_table':is_geography_table,
                'source_data_name':source_data_name,
                'metadata_id':metadata_id,
                'field_metadata_formset':field_metadata_formset,
                'has_delete_permission':has_delete_permission}

# Delete Metadata Entry
## Metadata entry delete confirm
@login_required
@render_to("dcmetadata/metadata_delete_confirm.html")
def metadata_delete_confirm(request,metadata_id):
    source_data = SourceDataInventory.objects.get(id=metadata_id)
    source_data_name = source_data.title

    return {'metadata_id':metadata_id,
            'source_data_name':source_data_name,
            }

## Delete Metadata entry
@login_required
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