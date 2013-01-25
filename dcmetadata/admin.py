from dcmetadata.models import *
from dcmetadata.forms import *
from django.contrib import admin

# Import from general utilities
from util import *

# Customized Admin Form for Look-up Table Model
## Macro Domain Admin
class MacroDomainAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(MacroDomain, MacroDomainAdmin)

## Subject Matter Admin
class SubjectMatterAdmin(admin.ModelAdmin):
    fields = ['name','macrodomain']
    list_display = ('id','name','macrodomain')
    list_filter = ['macrodomain']
    list_per_page = 10
    
admin.site.register(SubjectMatter, SubjectMatterAdmin)

## Geography Admin
class GeographyAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(Geography, GeographyAdmin)

## Coverage Admin
class CoverageAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(Coverage, CoverageAdmin)

## Format Admin
class FormatAdmin(admin.ModelAdmin):
    fields = ['name','extension']
    list_display = ('id','name','extension')
    list_per_page = 10
    
admin.site.register(Format, FormatAdmin)

## Source Admin
class SourceAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(Source, SourceAdmin)

## Visualization Type Admin
class VisualizationTypeAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(VisualizationType, VisualizationTypeAdmin)

## Spatial Table Admin
class SpatialTableAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(SpatialTable, SpatialTableAdmin)

## Tag Admin
class TagAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 10
    
admin.site.register(Tag,TagAdmin)

## Data Tables Admin
class DataTableAdmin(admin.ModelAdmin):
    fields = ['id','table_name','db_table']
    list_display = ('id','table_name','db_table')
    list_per_page = 10
    
admin.site.register(DataTable, DataTableAdmin)

# Customized Admin Form for Source Data Inventory Model
class SourceDataInventoryAdmin(admin.ModelAdmin):
    fields = ['upload_file','file_name','format','title','macro_domain','subject_matter',
        'coverage','geography','year','source','source_website','location','geometry',
        'description','data_consideration','process_notes']    
#    fields = ['upload_file','file_name','format','description','macro_domain','subject_matter',
#    'coverage','geography','begin_year','end_year','source','location','cleaning_notes']
    readonly_fields = ['file_name','format']
    list_display = ('title','macro_domain','subject_matter',
        'coverage','geography','year','source','_get_metadata_link')     
#    list_display = ('file_name','title','macro_domain','subject_matter',
#        'coverage','geography','year','source','format','_get_file_size','_get_metadata_link')
    list_filter = ['macro_domain','subject_matter','coverage','geography','source','year']    
#    list_filter = ['macro_domain','subject_matter','coverage','geography',
#    'format','source','begin_year','end_year']
    list_per_page = 10
    
    # By defualt use the Change page form
    form = SourceDataInventoryAdminChangeForm
    def get_form(self,request,obj=None,**kwargs):
        if not obj: # obj is None, this is ADD page, then use the Add page form
            self.form = SourceDataInventoryAdminAddForm
        return super(SourceDataInventoryAdmin,self).get_form(request,obj,**kwargs)
    
admin.site.register(SourceDataInventory, SourceDataInventoryAdmin)

# Table Metadata Admin
class TableMetadataAdmin(admin.ModelAdmin):
    fields = ['metadata']
    list_display = ['id','metadata']
    list_per_page = 10
    
admin.site.register(TableMetadata,TableMetadataAdmin)

# Admin for Dataset Model
class DatasetAdmin(admin.ModelAdmin):
    fields = ['id','nid','name','tables','tags','large_dataset']
    list_display = ('id','nid','name','_get_str_tables','_get_str_tags','_is_large_dataset','_get_metadata_link')
    list_filter = ['tags','tables']
    list_per_page = 10
    filter_horizontal = ['tables','tags']
    
admin.site.register(Dataset,DatasetAdmin)

# Dataset Metadata Admin
class DatasetMetadataAdmin(admin.ModelAdmin):
    fields = ['metadata']
    list_display = ['id','metadata']
    list_per_page = 10
    
admin.site.register(DatasetMetadata,DatasetMetadataAdmin)

## Metadata Admin
#class MetadataAdmin(admin.ModelAdmin):
#    fields = ['id','metadata']
#    readonly_fields = ['id']
#    list_display = ('id','_get_metadata_string','metadata')
#    
#    # By defualt use the Change page form
#    form = MetadataAdminChangeForm
#    def get_form(self,request,obj=None,**kwargs):
#        if not obj: # obj is None, this is ADD page, then use the Add page form
#            self.form = MetadataAdminAddForm
#        return super(MetadataAdmin,self).get_form(request,obj,**kwargs)