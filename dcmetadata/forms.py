from django.contrib import admin
from django import forms
from django.forms.widgets import *
from django.db import models

# Import from general utilities
from util import *

from dcmetadata.models import *

## Source Data Root Path in Inventory File
#SOURCE_DATA_ROOT_PATH_ORIGIN = 'G:\\'
#
## Source Data Root Path On Server "Pitondc1"
#SOURCE_DATA_ROOT_PATH_LOCAL = '\\\\pitondc1\\Departments\\Data\\'


# Custome SourceDataInventory Admin Model Form for CHANGE Page
class SourceDataInventoryAdminChangeForm(forms.ModelForm):
    upload_file = forms.FileField(required=False)

    def save(self, commit=True):
        model = super(SourceDataInventoryAdminChangeForm, self).save(commit=False)
        
        # Transform local path to server path
        if self.cleaned_data['location'].find(SOURCE_DATA_ROOT_PATH_ORIGIN) >= 0:
            model.location = self.cleaned_data['location'].replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)        
        
        if self.cleaned_data['upload_file'] != None:
            upload_file = self.cleaned_data['upload_file'].name
            upload_file_name = upload_file[:upload_file.index('.')]
            upload_file_extension = upload_file[upload_file.index('.')+1:]
            model.file_name = upload_file_name
            model.file_size = self.cleaned_data['upload_file'].size
            
            # Get the format for the file extension from lookup table "Format"
            try:
                # Full-text search on column Format
                q = upload_file_extension
                model.format = Format.objects.extra(
                    where=['ext_tsv @@ plainto_tsquery(%s)'],params=[q])[0]
            except:# Create new format if it dosenot exist
                add_format = Format(name=upload_file_extension,extension=upload_file_extension)
                add_format.save()
                model.format = Format.objects.get(extension=upload_file_extension)
        
        if commit:
            model.save()
            
        return model
    
    class Meta:
        model = SourceDataInventory
        
# Custome SourceDataInventory Admin Model Form for ADD page
class SourceDataInventoryAdminAddForm(forms.ModelForm):
    upload_file = forms.FileField(required=True)

    def save(self, commit=True):
        model = super(SourceDataInventoryAdminAddForm, self).save(commit=False)
        
        if self.cleaned_data['upload_file'] != None:
            upload_file = self.cleaned_data['upload_file'].name
            upload_file_name = upload_file[:upload_file.index('.')]
            upload_file_extension = upload_file[upload_file.index('.')+1:]
            model.file_name = upload_file_name
            model.file_size = self.cleaned_data['upload_file'].size
            if self.cleaned_data['location'].find(SOURCE_DATA_ROOT_PATH_ORIGIN) >= 0:
                model.location = self.cleaned_data['location'].replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)
                
            # Get the format for the file extension from lookup table "Format"
            try:
                # Full-text search on column Format
                q = upload_file_extension
                model.format = Format.objects.extra(
                    where=['ext_tsv @@ plainto_tsquery(%s)'],params=[q])[0]
            except:# Create new format if it dosenot exist
                add_format = Format(name=upload_file_extension,extension=upload_file_extension)
                add_format.save()
                model.format = Format.objects.get(extension=upload_file_extension)
        
        if commit:
            model.save()
            
        return model
    
    class Meta:
        model = SourceDataInventory
        
        
# Custome Metadata Admin Model Form for CHANGE Page
class MetadataAdminChangeForm(forms.ModelForm):
    
    class Meta:
        model = Metadata
        
# Custom Metadata Admin Model Form for ADD Page
class MetadataAdminAddForm(forms.ModelForm):
    
    class Meta:
        model = Metadata

# Multi Widget
class SplitTagWidget(MultiWidget):
#    def __init__(self,attrs=None,value):
#        widgets = tuple([TextInput(attrs=None) for i in value[:-1].split(";")])
#        super(SplitTagWidget,self).__init__(widgets,attrs)
        
    def decompress(self, value):
        if value:
            return value[:-1].split(";")
        return [None for i in value[:-1].split(";")]
    
    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)

# Metadata Field Form
class MetadataFieldForm(forms.Form):
    field_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}))
    data_type = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':6}))
    tags = forms.MultiValueField(widget=SplitTagWidget())
    
    class Meta:
        fields = ('field_name','data_type','description','tags')