from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.auth.views import logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('outcomesandstrategiesmanagement.views',
	# Home page URL
	url(r'^home/$','home'),
	
	# Login,Logout,Register,User
	url(r'^login/$','user_login'),
	url(r'^logout/$',logout,{'template_name': 'registration/logged_out.html'}),
	url(r'^register/$','register'),
	url(r'^user/profile/$','user_profile'),
	url(r'^user/password/$','user_change_password'),
#	url(r'^logout/$',logout,{'template_name': 'registration/logged_out.html', 'next_page':'../login/'}),

	# Budget
	url(r'activity/(?P<activity_id>\d+)/budget_list/$','activity_budget_list'),

	# Master Download
	url(r'masterdownload/csv/$','masterdownload_csv'),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)