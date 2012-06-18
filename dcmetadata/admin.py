from dcmetadata.models import *
from django.contrib import admin

# Customized Admin Form for Look-up Table Model
## Macro Domain Admin
class MacroDomainAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    
admin.site.register(MacroDomain, MacroDomainAdmin)

## Subject Matter Admin
class SubjectMatterAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    
admin.site.register(SubjectMatter, SubjectMatterAdmin)

## Geography Admin
class GeographyAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    
admin.site.register(Geography, GeographyAdmin)

## Coverage Admin
class CoverageAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    
admin.site.register(Coverage, CoverageAdmin)

## Format Admin
class FormatAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    
admin.site.register(Format, FormatAdmin)

## Source Admin
class SourceAdmin(admin.ModelAdmin):
    fields = ['id','name']
    list_display = ('id','name')
    
admin.site.register(Source, SourceAdmin)


# Customized Admin Form for Source Data Inventory Model
class SourceDataInventoryAdmin(admin.ModelAdmin):
    fields = ['file_name','description','macro_domain','subject_matter',
    'coverage','geography','begin_year','end_year','format','source','location']
    list_display = ('file_name','description','macro_domain','subject_matter',
    'coverage','geography','_get_year_range','source','format','_get_file_size')
    list_filter = ['macro_domain','subject_matter','coverage','geography',
    'format','source','begin_year','end_year']

admin.site.register(SourceDataInventory, SourceDataInventoryAdmin)