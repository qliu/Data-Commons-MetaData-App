from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('dcmetadata.views',

	# Metadata URLs
	url(r'^metadata/(?P<metadata_id>\d+)/$','metadata_detail'),
	url(r'^metadata/(?P<metadata_id>\d+)/edit/$','metadata_edit'),
	url(r'^metadata/(?P<metadata_id>\d+)/delete_confirm/$','metadata_delete_confirm'),
	url(r'^metadata/(?P<metadata_id>\d+)/delete/$','metadata_delete'),
	
	# Admin AJAX URLs
	url(r'^admin/ajax_get_subjectmatter/','ajax_get_subjectmatter'),

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