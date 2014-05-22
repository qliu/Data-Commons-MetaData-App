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
                if "next" in request.GET:
                    app_name = request.GET["next"].replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    url = request.META["HTTP_REFERER"]
                    if url.partition("/?next=/")[1] == "":
                        if APP_SERVER_URL == "":
                            # a trick for localhost
                            app_name = url.partition("http://")[2].replace(SERVER_URL,"").partition("/")[2].partition("/")[0]
                        else:
                            app_name = url.partition("http://")[2].replace(SERVER_URL,"").replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                    else:
                        app_name = url.partition("/?next=/")[2].partition("/")[0]
                    return HttpResponseRedirect('%s/%s/home/' % (APP_SERVER_URL,app_name))                
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
            if "next" in request.GET:
                app_name = request.GET["next"].replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                return HttpResponseRedirect(request.GET["next"])
            else:
                url = request.META["HTTP_REFERER"]
                print url
                if url.partition("/?next=/")[1] == "":
                    if APP_SERVER_URL == "":
                        # a trick for localhost
                        app_name = url.partition("http://")[2].replace(SERVER_URL,"").partition("/")[2].partition("/")[0]
                    else:
                        app_name = url.partition("http://")[2].replace(SERVER_URL,"").replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                else:
                    app_name = url.partition("/?next=/")[2].partition("/")[0]
                return HttpResponseRedirect('%s/%s/home/' % (APP_SERVER_URL,app_name))            
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
                if "next" in request.GET:
                    app_name = request.GET["next"].replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    url = request.META["HTTP_REFERER"]
                    if url.partition("/?next=/")[1] == "":
                        if APP_SERVER_URL == "":
                            # a trick for localhost
                            app_name = url.partition("http://")[2].replace(SERVER_URL,"").partition("/")[2].partition("/")[0]
                        else:
                            app_name = url.partition("http://")[2].replace(SERVER_URL,"").replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                    else:
                        app_name = url.partition("/?next=/")[2].partition("/")[0]
                    return HttpResponseRedirect('%s/%s/home/' % (APP_SERVER_URL,app_name))                                
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

'''-----------------------
Content Views
-----------------------'''
@login_required
@render_to("outcomesandstrategiesmanagement/activity_budget_list.html")
def activity_budget_list(quest,activity_id):
    activity = Activity.objects.get(id=activity_id)
    budgets = Budget.objects.filter(activity=activity_id)
    total_budget = activity._get_total_budget
    return {
            "activity_id":activity_id,
            "activity":activity,
            "total_budget":total_budget,
            "budgets":budgets,
    }

'''----------------------
Download Admin List View
----------------------'''
# Export as CSV
def export_csv(queryset,fields=None,field_names=None):
    model = queryset.model
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % slugify(model.__name__)
    writer = csv.writer(response)
    
    # write headers
    if field_names:
        headers = fields
        header_names = field_names
    else:
        headers = []
        header_names = []
        for field in model._meta.fields:
            headers.append(field.name)
            header_names.append(field.name)
    writer.writerow(header_names)
    
    # write rows
    for obj in queryset:
        row = []
        for field in headers:
            if field in headers:
                if field.startswith("_"):
                    # object method
                    val = getattr(obj,field)()
                else:
                    # object property
                    val = getattr(obj,field)
                if type(val) == unicode:
                    val = val.encode("utf-8")
                row.append(val)
        writer.writerow(row)
    return response
        
# Download Admin List View
@login_required
def download_admin_list_view(request,app_label,model_name,format,queryset=None,fields=None,list_display=True):   
    if not request.user.is_staff:
        return HttpResponseForbidden()
    else:
        if not queryset:
            model = get_model(app_label,model_name)
            queryset = model.objects.all()
            filters = dict()
            url_query_str = request.META["HTTP_REFERER"].partition("/?")[2]
            filter_str_list = url_query_str.split("&")
            for filter_str in filter_str_list:
                f = filter_str.split("=")
                filters[f[0]]=f[1]
            if len(filters):
                queryset = queryset.filter(**filters)
        if not fields and list_display:
            list_display = admin.site._registry[queryset.model].list_display
            if list_display and len(list_display) > 0:
                fields = list_display
                field_names = admin.site._registry[queryset.model].list_display_field_names
            else:
                fields = None
            if format == "csv":
                return export_csv(queryset,fields,field_names)
            else:
                return HttpResponseForbidden()