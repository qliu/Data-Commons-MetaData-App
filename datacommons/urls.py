from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

## import dajaxice core
#from dajaxice.core import dajaxice_autodiscover
#dajaxice_autodiscover()

urlpatterns = patterns('',

	# Data Commons MetaData App Tabble Upload URLs
	#(r'^datacommons/sourcedata/$','dcmetadata.views.sourcedata'),
	
	## Upload lookup tables
	### Upload standard lookup talbes
	url(r'^lookuptable/standard_upload/$','dcmetadata.views.upload_standard_lookup_tables'),
	### Upload other lookup tables
	url(r'^lookuptalbe/format_upload/$','dcmetadata.views.upload_lookup_table_format'),
	
	### Convert XML metadata to JSON metadata
	url(r'^xml2json/$','dcmetadata.views.xml2json'),
	
	### Convert all name to id for foreign keys in table metadata
	url(r'^fkeyname2id/$','dcmetadata.views.fkeyname2id'),
	
	### Convert all id to name for foreign keys in table metadata
	url(r'^fkeyid2name/$','dcmetadata.views.fkeyid2name'),	
	
	### Copy Table Tags from Source Data Inventory
	url(r'^maketabletags/$','dcmetadata.views.maketabletags'),
	
	## Upload source data inventory
	url(r'^sourcedata/upload/$','dcmetadata.views.upload_sourcedata'),
	
	# Data Commons MetaData App URLs
	url(r'^dcmetadata/',include('dcmetadata.urls')),
	
	# Help Document page of PyQt4 GUI tool for uploading Excel table to database
	url(r'^db_upload_help_doc/$','dcmetadata.views.db_upload_help_doc'),	

    # Examples:
    # url(r'^$', 'datacommons.views.home', name='home'),
    # url(r'^datacommons/', include('datacommons.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	
#	# URLs for Dajaxice
#	url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)
