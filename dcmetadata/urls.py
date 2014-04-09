from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.auth.views import logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('dcmetadata.views',
	# Home page URL
	url(r'^home/$','home'),
	
	# Login,Logout,Register,User
	url(r'^login/$','user_login'),
	url(r'^logout/$',logout,{'template_name': 'registration/logged_out.html'}),
	url(r'^register/$','register'),
	url(r'^user/profile/$','user_profile'),
	url(r'^user/password/$','user_change_password'),
#	url(r'^logout/$',logout,{'template_name': 'registration/logged_out.html', 'next_page':'../login/'}),

	# Table Metadata URLs
	url(r'^metadata/(?P<metadata_id>\d+)/$','metadata_detail'),
	url(r'^metadata/(?P<metadata_id>\d+)/edit/$','metadata_edit'),
	url(r'^metadata/(?P<metadata_id>\d+)/delete_confirm/$','metadata_delete_confirm'),
	url(r'^metadata/(?P<metadata_id>\d+)/delete/$','metadata_delete'),
	
	# Dataset URLs
	url(r'^dataset/metadata/(?P<dataset_id>\d+)/$','dataset_metadata_detail'),
	url(r'^dataset/metadata/(?P<dataset_id>\d+)/edit/$','dataset_metadata_edit'),
	url(r'^dataset/metadata/(?P<dataset_id>\d+)/delete_confirm/$','dataset_metadata_delete_confirm'),
	url(r'^dataset/metadata/(?P<dataset_id>\d+)/delete/$','dataset_metadata_delete'),
	
	# Export Source Data
	## Download Source Data
	url(r'^sourcedatainventory/(?P<sourcedata_id>\d+)/download/$','download_sourcedata'),
	## Add Query Layer in ArcGIS
	url(r'^sourcedatainventory/(?P<sourcedata_id>\d+)/add_querylayer/$','instruction_add_querylayer'),
	
	# Import Data from Metadata URLs
	url(r'^import/dataset/','import_dataset'),
	url(r'^import/sourcedata/','import_sourcedata'),
	
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
	url(r'^test/tagsname2id/$','tagsname2id'),
	url(r'^test/addupdatedate/$','addupdatedate'),
	
	# test Dajaxice URLs
	url(r'^test/test_dajaxice/$','test_dajaxice'),
)