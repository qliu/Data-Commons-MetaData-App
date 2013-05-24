from django.contrib import admin
from django import forms
from django.forms.widgets import *
from django.db import models
from django.forms.formsets import formset_factory, BaseFormSet
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

# Snippet import to use the admin FilterSelectMultiple widget in normal forms
from django.contrib.admin.widgets import FilteredSelectMultiple

# Import from general utilities
from util import *

from dcmetadata.models import *

## Source Data Root Path in Inventory File
#SOURCE_DATA_ROOT_PATH_ORIGIN = 'G:\\'
#
## Source Data Root Path On Server "Pitondc1"
#SOURCE_DATA_ROOT_PATH_LOCAL = '\\\\pitondc1\\Departments\\Data\\'

# User Forms
class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ('groups','is_staff','is_active','is_superuser','user_permissions','last_login','date_joined',)    

# Custome SourceDataInventory Admin Model Form for CHANGE Page
class SourceDataInventoryAdminChangeForm(forms.ModelForm):
    upload_file = forms.FileField(required=False)
    location = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}),required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':6}),required=False)
    data_consideration = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':6}),required=False)
    process_notes = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':10}),required=False)
#    macro_domain = forms.ModelChoiceField(queryset=MacroDomain.objects.all(),widget=forms.Select(attrs={'onchange':'get_subjectmatter();'}))

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
                ## Need PostgreSQL Setup:
                ## 1. Add a column to hold a tsvector
                ##    ALTER TABLE inventory_format ADD COLUMN ext_tsv tsvector;
                ## 2. Add a trigger to update the ext_tsv column whenever a record is inserted or updated
                ##    CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE ON inventory_format FOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger(ext_tsv, 'pg_catalog.english', extension);
                ## 3. Create an index on ext_tsv to make searches more efficient
                ##    CREATE INDEX inventory_format_ext_tsv ON inventory_format USING gin(ext_tsv);
                ## 4. If there is already rechords in the inventory_format table, update the ext_tsv for those records
                ##    UPDATE inventory_format SET ext_tsv=to_tsvector(extension);
                ## 5. SQL example
                ##    SLECT extension FROM inventory_format WHERE ext_tsv @@ plainto_tsquery('serch words');
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
    upload_file = forms.FileField(required=False)
    location = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=True)
    title = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}),required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':6}),required=False)
    data_consideration = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':6}),required=False)
    process_notes = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':10}),required=False)
#    macro_domain = forms.ModelChoiceField(queryset=MacroDomain.objects.all(),widget=forms.Select(attrs={'onchange':'get_subjectmatter();'})) 

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

# Field Metadata Form
class FieldMetadataForm(forms.Form):
    field_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
    data_type = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    verbose_name = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    no_data_value = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=False)
    
    # Field tags form:
    geography = forms.ModelChoiceField(queryset=Coverage.objects.all(),required=False)
    geographic_level = forms.ModelChoiceField(queryset=Geography.objects.all(),required=False)
    domain = forms.ModelChoiceField(queryset=MacroDomain.objects.all(),required=False)
    subdomain = forms.ModelChoiceField(queryset=SubjectMatter.objects.all(),required=False)
    year = forms.ChoiceField(widget=forms.Select(),choices=YEAR_CHOICES,required=False)
    visualization_types = forms.ModelMultipleChoiceField(queryset=VisualizationType.objects.all(),required=False)
    geometry = forms.ModelChoiceField(queryset=SpatialTable.objects.all(),required=False)    
    
    class Meta:
        fields = ('field_name','data_type','verobse_name','no_data_value')

# Field Metadata Formset
FieldMetadataFormset = formset_factory(FieldMetadataForm,extra=0)

# File Upload Form
class FileUploadForm(forms.Form):
    upload_file = forms.FileField(required=False)
    
# Dataset Form
class DatasetForm(forms.ModelForm):
#    id = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'size':'10'}),required=True)
#    nid = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'size':'10'}),required=True)

    class Meta:
        model = Dataset
        widgets = {
                    "id": forms.TextInput(attrs={'size':'10'}),
                    "nid": forms.TextInput(attrs={'size':'10'}),
        }
    
# Dataset Metadata Form
class DatasetMetadataForm(forms.Form):
    fields = forms.MultipleChoiceField()
    display_name = forms.ChoiceField()
    pkey = forms.MultipleChoiceField()
    gkey_main  = forms.ChoiceField()
    gkey_spatial = forms.ChoiceField()
    
    def clean(self):
        '''
        Check that selected value is not "None" which is form list seperator
        '''
        if any(self.errors):
            # Validiating the form unless each field is valid on its own
            return
        cleaned_data = self.cleaned_data
        fields = cleaned_data["fields"]
        display_name = cleaned_data["display_name"]
        gkey_main = cleaned_data["gkey_main"]
        gkey_spatial = cleaned_data["gkey_spatial"]
        pkey = cleaned_data["pkey"]
        form_has_error = False
        msg = "Table title is selected! Please select a field instead."
        if "None" in fields:
            self._errors["fields"] = self.error_class([msg])
            form_has_error = True
        if display_name == "None":
            self._errors["display_name"] = self.error_class([msg])
            form_has_error = True
        if gkey_main == "None":
            self._errors["gkey_main"] = self.error_class([msg])
            form_has_error = True
        if gkey_spatial == "None":
            print "gkey SPATIAL ERROR"
            self._errors["gkey_spatial"] = self.error_class([msg])
            form_has_error = True
        if "None" in pkey:
            self._errors["pkey"] = self.error_class([msg])
            form_has_error = True
        if form_has_error:
            raise forms.ValidationError("Table title is selected!")
        
        return cleaned_data
        
    
## Dataset Metadata Foreign Key Formset
class DatasetMetadataFKeyForm(forms.Form):
    foreign_key = forms.ChoiceField()
    reference_key = forms.ChoiceField()
    
## Set BaseDatasetMetadataFKeyFormSet with custom formset valication
class BaseDatasetMetadataFKeyFormSet(BaseFormSet):
    def clean(self):
        '''
        Check that selected value is not "None" which is form list seperator,
            and that foreign_key and reference_key are from different tables
        '''
        if any(self.errors):
            # Validating the formset unless each form is valid on its own
            return
        for i in range(0,self.total_form_count()):
            form = self.forms[i]
            fk = form.cleaned_data['foreign_key']
            rk = form.cleaned_data['reference_key']
            if fk == "None" or rk == "None":
                if fk == "None":
                    form._errors["foreign_key"] = form.error_class(["Table title is selected! Please select a foreign key instead."])
                if rk == "None":
                    form._errors["reference_key"] = form.error_class(["Table title is selected! Please select a reference key instead."])
                raise forms.ValidationError("Key is NONE")                
            else:
                if fk[:fk.find('.')] == rk[:rk.find('.')]:
                    form._errors["foreign_key"] = form.error_class(["Foreign Key and Reference Key must from different tables."])
                    form._errors["reference_key"] = form.error_class(["Foreign Key and Reference Key must from different tables."])
                    raise forms.ValidationError("Foreign Key and Reference Key from same table")
        

DatasetMetadataFKeyFormSet = formset_factory(DatasetMetadataFKeyForm,extra=0,formset=BaseDatasetMetadataFKeyFormSet)
    
## Metadata Field Form
#class MetadataFieldForm(forms.Form):
#    field_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
#    data_type = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'size':'50'}),required=False)
#    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
#    tags = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}),required=False,help_text='Seperate tags with semicolon. (Example: tag1;tag2;)')
#    
#    class Meta:
#        fields = ('field_name','data_type','description','tags')
#
#          
## Metadata Fields Formset
#MetadataFieldsFormset = formset_factory(MetadataFieldForm,extra=0)
#  
## Custome Metadata Admin Model Form for CHANGE Page
#class MetadataAdminChangeForm(forms.ModelForm):
#    
#    class Meta:
#        model = Metadata
# 
## Custom Metadata Admin Model Form for ADD Page
#class MetadataAdminAddForm(forms.ModelForm):
#    
#    class Meta:
#        model = Metadata
# 
## Metadata Other Information Form
#class MetadataOtherForm(forms.Form):
#    info_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
#    info_value = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
#    
## Metadata Other Information Formset
#MetadataOtherFormset = formset_factory(MetadataOtherForm,extra=0)
# 
## Metadata Attribute Tag Form
#class MetadataAttributeTagForm(forms.Form):
#    domain = forms.ModelChoiceField(queryset=MacroDomain.objects.all(),required=False)
#    sub_domain = forms.ModelChoiceField(queryset=SubjectMatter.objects.all(),required=False)
#    begin_year = forms.ChoiceField(widget=forms.Select(),choices = YEAR_CHOICES,required=False)
#    end_year = forms.ChoiceField(widget=forms.Select(),choices = YEAR_CHOICES,required=False)
#    visualization_types = forms.ModelChoiceField(queryset=VisualizationType.objects.all(),required=False)
#    # How geomertry links to spatial dataset (locations) will be determined later
#    geometry = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'size':'50'}),required=False)
#    
## Metadata Attribute Tag Formset
#MetadataAttributeTagFormset = formset_factory(MetadataAttributeTagForm,extra=0)
#
## Fields Metadata Form
#class FieldsMetadataForm(forms.Form):
#    field_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'50'}),required=True)
#    data_type = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'size':'50'}),required=False)
#    description = forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':3}),required=False)
#    
#    class Meta:
#        fields = ('field_name','data_type','description')
#        
## Metadata Fields Formset
#FieldsMetadataFormset = formset_factory(FieldsMetadataForm,extra=0)