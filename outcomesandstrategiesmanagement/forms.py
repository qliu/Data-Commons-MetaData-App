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