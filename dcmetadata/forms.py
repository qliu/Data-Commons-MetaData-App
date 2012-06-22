from django.contrib import admin
from django import forms
from django.db import models
from dcmetadata.models import *
import os

from dcmetadata.views import SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL

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
        
        if self.cleaned_data['upload_file'] != None:
            upload_file = self.cleaned_data['upload_file'].name
            upload_file_name = upload_file[:upload_file.index('.')]
            upload_file_extension = upload_file[upload_file.index('.')+1:]
            model.file_name = upload_file_name
            model.file_size = self.cleaned_data['upload_file'].size
            if self.cleaned_data['location'].find(SOURCE_DATA_ROOT_PATH_ORIGIN) >= 0:
                model.location = self.cleaned_data['location'].replace(SOURCE_DATA_ROOT_PATH_ORIGIN,SOURCE_DATA_ROOT_PATH_LOCAL)
            # Create new format if it dosenot exist
            try:
                model.format = Format.objects.get(extension=upload_file_extension)
            except:
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
            # Create new format if it dosenot exist
            try:
                model.format = Format.objects.get(extension=upload_file_extension)
            except:
                add_format = Format(name=upload_file_extension,extension=upload_file_extension)
                add_format.save()
                model.format = Format.objects.get(extension=upload_file_extension)
        
        if commit:
            model.save()
            
        return model
    
    class Meta:
        model = SourceDataInventory