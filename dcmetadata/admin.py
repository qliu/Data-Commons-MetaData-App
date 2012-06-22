from dcmetadata.models import *
from django.contrib import admin
from dcmetadata.forms import *

# Customized Admin Form for Look-up Table Model
## Macro Domain Admin
class MacroDomainAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    
admin.site.register(MacroDomain, MacroDomainAdmin)

## Subject Matter Admin
class SubjectMatterAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    
admin.site.register(SubjectMatter, SubjectMatterAdmin)

## Geography Admin
class GeographyAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    
admin.site.register(Geography, GeographyAdmin)

## Coverage Admin
class CoverageAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    
admin.site.register(Coverage, CoverageAdmin)

## Format Admin
class FormatAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    
admin.site.register(Format, FormatAdmin)

## Source Admin
class SourceAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    
admin.site.register(Source, SourceAdmin)

# Customized Admin Form for Source Data Inventory Model
class SourceDataInventoryAdmin(admin.ModelAdmin):
    fields = ['upload_file','file_name','format','description','macro_domain','subject_matter',
    'coverage','geography','begin_year','end_year','source','location']
    readonly_fields = ['file_name','format']
    list_display = ('file_name','description','macro_domain','subject_matter',
    'coverage','geography','_get_year_range','source','format','_get_file_size')
    list_filter = ['macro_domain','subject_matter','coverage','geography',
    'format','source','begin_year','end_year']
    # By defualt use the Change page form
    form = SourceDataInventoryAdminChangeForm
    def get_form(self,request,obj=None,**kwargs):
        if not obj: # obj is None, this is ADD page
            self.form = SourceDataInventoryAdminAddForm
        return super(SourceDataInventoryAdmin,self).get_form(request,obj,**kwargs)
    
admin.site.register(SourceDataInventory, SourceDataInventoryAdmin)