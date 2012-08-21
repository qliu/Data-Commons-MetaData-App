from django.contrib import admin
from django import forms
from django.forms.widgets import *
from django.db import models
from django.forms.formsets import formset_factory

# Import from general utilities
from util import *

from dcmetadata.models import *

## Source Data Root Path in Inventory File
#SOURCE_DATA_ROOT_PATH_ORIGIN = 'G:\\'
#
## Source Data Root Path On Server "Pitondc1"
#SOURCE_DATA_ROOT_PATH_LOCAL = '\\\\pitondc1\\Departments\\Data\\'

# Choices
YEAR_CHOICES = tuple((i,i) for i in range (1980,2013))


# Custome SourceDataInventory Admin Model Form for CHANGE Page
class SourceDataInventoryAdminChangeForm(forms.ModelForm):
    upload_file = forms.FileField(required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
    location = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=True)

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
    location = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))

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

# Metadata Field Form
class MetadataFieldForm(forms.Form):
    field_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
    data_type = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}),required=False,help_text='Seperate tags with semicolon. (Example: tag1;tag2;)')
    
    class Meta:
        fields = ('field_name','data_type','description','tags')
        
# Metadata Fields Formset
MetadataFieldsFormset = formset_factory(MetadataFieldForm,extra=0)

# Metadata Other Information Form
class MetadataOtherForm(forms.Form):
    info_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
    info_value = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
    
# Metadata Other Information Formset
MetadataOtherFormset = formset_factory(MetadataOtherForm,extra=0)

# Metadata Attribute Tag Form
class MetadataAttributeTagForm(forms.Form):
    domain = forms.ModelChoiceField(queryset=MacroDomain.objects.all(),required=False)
    sub_domain = forms.ModelChoiceField(queryset=SubjectMatter.objects.all(),required=False)
    begin_year = forms.ChoiceField(widget=forms.Select(),choices = YEAR_CHOICES,required=False)
    end_year = forms.ChoiceField(widget=forms.Select(),choices = YEAR_CHOICES,required=False)
    visualization_type = forms.ModelChoiceField(queryset=VisualizationType.objects.all(),required=False)
    # How geomertry links to spatial dataset (locations) will be determined later
    geometry = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    
# Metadata Attribute Tag Formset
MetadataAttributeTagFormset = formset_factory(MetadataAttributeTagForm,extra=0)

# Fields Metadata Form
class FieldsMetadataForm(forms.Form):
    field_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
    data_type = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
    
    class Meta:
        fields = ('field_name','data_type','description')
        
# Metadata Fields Formset
FieldsMetadataFormset = formset_factory(FieldsMetadataForm,extra=0)

# File Upload Form
class FileUploadForm(forms.Form):
    upload_file = forms.FileField(required=False)