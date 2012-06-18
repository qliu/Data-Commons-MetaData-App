from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# import dajaxice core
from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

urlpatterns = patterns('',

	# Data Commons MetaData App URLs
	#(r'^datacommons/sourcedata/$','dcmetadata.views.sourcedata'),
	url(r'^datacommons/sourcedata/upload/$','dcmetadata.views.upload_sourcedata'),
	url(r'^datacommons/metadata/',include('dcmetadata.urls')),

    # Examples:
    # url(r'^$', 'datacommons.views.home', name='home'),
    # url(r'^datacommons/', include('datacommons.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	
	# URLs for Dajaxice
	url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	
	# test Dajaxice URLs
	url(r'^test/test_dajaxice/$','dcmetadata.views.test_dajaxice'),
)
