from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('dcmetadata.views',

	# Metadata URLs goes here
	#(r'^datacommons/metadata/','datacommons.DCmetadata.views.'),

    # Examples:
    # url(r'^$', 'datacommons.views.home', name='home'),
    # url(r'^datacommons/', include('datacommons.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
	
	
	# Test URLs:
	url(r'^test/$','test'),
	
	# test Dajaxice URLs
	url(r'^test/test_dajaxice/$','test_dajaxice'),
)