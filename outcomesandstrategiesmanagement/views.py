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

from outcomesandstrategiesmanagement.models import *
from outcomesandstrategiesmanagement.forms import *

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
                return HttpResponseRedirect('%s/outcomesandstrategiesmanagement/home/' % APP_SERVER_URL)
        else:
            error_msg = "Incorrect username or password."
            return {'error_msg':error_msg,'form':authform,'title':title}
    else:
        authform = AuthenticationForm()
        return {'form':authform,'title':title}
    
# Register
@render_to("outcomesandstrategiesmanagement/register.html")
def register(request):
    if request.method == 'POST':
        signup_form = UserCreationForm(request.POST)
        if signup_form.is_valid():
            new_user = signup_form.save()
            user = authenticate(username=signup_form.cleaned_data["username"], password=signup_form.cleaned_data["password2"])
            login(request, user)
            return HttpResponseRedirect('%s/outcomesandstrategiesmanagement/user/profile/' % APP_SERVER_URL)
        else:
            error_msg = "Please check your register information."
            return {'title':"Sign up",'error_msg':error_msg,'signup_form':signup_form}
    else:
        signup_form = UserCreationForm()
    return {'title':"Sign up",'signup_form':signup_form}


# User Profile
@login_required
@render_to("outcomesandstrategiesmanagement/user_profile.html")
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
                return HttpResponseRedirect('%s/outcomesandstrategiesmanagement/home/' % APP_SERVER_URL)
        else:
            messages.error(request, "Please correct the errors below.")
    return {'user_name':user.username,'user_profile_form':user_profile_form}

# User Change Password
@login_required
@render_to("outcomesandstrategiesmanagement/user_password.html")
def user_change_password(request):
    user = request.user
    if request.method == 'GET':
        user_password_form = PasswordChangeForm(user)
    elif request.method == 'POST':
        user_password_form = PasswordChangeForm(user,request.POST)
        if user_password_form.is_valid():
            user_password_form.save()
            messages.info(request, "User password was changed successfully.")
            return HttpResponseRedirect('%s/outcomesandstrategiesmanagement/user/profile/' % APP_SERVER_URL)
        else:
            messages.error(request, "Please correct the errors below.")
    return {'user_name':user.username,'user_password_form':user_password_form}

'''-----------------------
Home Page
-----------------------'''
# Home page
@login_required
@render_to("outcomesandstrategiesmanagement/home.html")
def home(request):
    return {}
