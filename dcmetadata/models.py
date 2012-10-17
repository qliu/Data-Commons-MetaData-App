from django.db import models
from django.contrib import admin
from django.core import serializers
from django.db.models.signals import post_save

# Import from general utilities
from util import *

# Choices
year_choices_list = [(None,"---------"),(0,"No Data")]
for i in range (1980,2013):
	year_choices_list.append((i,str(i)))
YEAR_CHOICES = tuple(year_choices_list)

# Look-up tables:
## Macro Domain
class MacroDomain(models.Model):
	'''
	Store macro domain of the source data
	'''
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		db_table = u'inventory_macrodomain'
		ordering = ['name']
		
## Subject Matter
class SubjectMatter(models.Model):
	'''
	Store subject of the source data
	'''	
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	macrodomain = models.ForeignKey('MacroDomain')
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		db_table = u'inventory_subjectmatter'
		ordering = ['name']
		
## Geography
class Geography(models.Model):
	'''
	Store geographic scale/level of the source data
	'''	
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		db_table = u'inventory_geography'
		ordering = ['name']
		
## Coverage
class Coverage(models.Model):
	'''
	Store geographic coverage of the source data
	'''	
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		db_table = u'inventory_coverage'
		ordering = ['name']
		
## Format
class Format(models.Model):
	'''
	Store data format of the source data
	'''	
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=20)
	extension = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		db_table = u'inventory_format'
		ordering = ['name']
		
## Source
class Source(models.Model):
	'''
	Store source of the source data
	'''
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		db_table = u'inventory_source'
		ordering = ['name']

## Visualization Type
class VisualizationType(models.Model):
	'''
	Store visualization types for attribute
	'''
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		db_table = u'visualization_type'
		ordering = ['name']
		
# Spatial Table Model
class SpatialTable(models.Model):
	'''
	Store Spatial table ID and name that can be linked to field goemetry
	'''
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

	class Meta:
		db_table = u'spatial_table'
		ordering = ['name']

# Handler After SourceDataInventory Model instance being saved
def post_save_handler_add_tabletags(sender,instance=True,**kwargs):
	metadata_id = instance.id
	if len(TableMetadata.objects.filter(id=metadata_id)) == 0:
		json_field_metadata = []
	else:
		table_metadata = TableMetadata.objects.get(id=metadata_id)
		metadata_json = table_metadata.metadata
		metadata_json_dict = table_metadata._get_metadata_dict()
		json_field_metadata = metadata_json_dict["field_metadata"]
		
	json_table_tags = {"title":instance.title,
					   "geography":instance.coverage.id,
					   "geographic_level":instance.geography.id,
					   "domain":instance.macro_domain.id,
					   "subdomain":instance.subject_matter.id,
					   "source":instance.source.id,
					   "year":instance.year,
					   "geometry":instance.geometry.id,
					   "description":instance.description,
					   "data_consideration":instance.data_consideration,
#						   "time_period":"%d;%d" % (instance.begin_year if instance.begin_year != None else 0,instance.end_year if instance.end_year != None else 0)
					  }
		
	json_root_dict = {"table_tags":json_table_tags,
					  "field_metadata":json_field_metadata}            
	json_metadata = json.dumps(json_root_dict)
	output_metadata = TableMetadata(id=metadata_id,metadata=json_metadata)
	output_metadata.save()
		
# Source Data Inventory Model
class SourceDataInventory(models.Model):
	"""
	Inventory of the source data.
	"""	
#	id = models.IntegerField(primary_key=True)
	file_name = models.CharField(max_length=200, verbose_name='File Name')
	title = models.CharField(max_length=200, null=True, blank=True)
	macro_domain = models.ForeignKey('MacroDomain',verbose_name='Macro Domain')
	subject_matter = models.ForeignKey('SubjectMatter',verbose_name='Subject Matter')
	year = models.IntegerField(verbose_name='Year',choices=YEAR_CHOICES,null=True)
#	begin_year = models.IntegerField(verbose_name='Begin Year',choices=YEAR_CHOICES,null=True)
#	end_year = models.IntegerField(verbose_name='End Year',choices=YEAR_CHOICES,null=True)
	geography = models.ForeignKey('Geography')
	coverage = models.ForeignKey('Coverage')
	source = models.ForeignKey('Source')
	format = models.ForeignKey('Format',null=True,blank=True)
	location =  models.CharField(max_length=200)
	file_size = models.FloatField(default=0,verbose_name='File Size',null=True, blank=True)
	metadata = models.ForeignKey('TableMetadata',null=True,blank=True)
	geometry = models.ForeignKey('SpatialTable',verbose_name='Spatial Table')
	description = models.CharField(max_length=500, null=True, blank=True)
	data_consideration = models.CharField(max_length=500, null=True, blank=True)
	process_notes = models.CharField(max_length=5000, null=True, blank=True)
	
	def __unicode__(self):
		'''
		Return file name as default for inventory entry
		'''
		return self.file_name
	
#	def _get_year_range(self):
#		'''
#		Return year range from begin_year to end_year
#		'''
#		begin_year = self.begin_year
#		end_year = self.end_year
#		if begin_year != None and end_year != None:
#			if begin_year <= end_year:
#				return '%d-%d' % (begin_year, end_year)
#			else:
#				return 'Invalid Year Range'
#		else:
#			return 'No Data'
#		
#	_get_year_range.short_description = "Dates"
#	_get_year_range.admin_order_field = "begin_year"
	
#	def is_within_year_range(self,year):
#		'''
#		Return True if year is within year range
#		'''
#		return self.begin_year <= year and year <= self.end_year
	
	def _get_file_size(self):
		'''
		Return human readable presentation of file size in bytes
		'''
		return HumanReadableSize(self.file_size,FILE_SIZE_PRECISION)
		
	_get_file_size.short_description = "File Size"
	
		
	def _get_metadata_link(self):
		'''
		Return HTML link for view and edit metadata associated with record
		'''
		if self.metadata != None:
			return '<a href="%s/dcmetadata/metadata/%d/" target="_blank">View</a> <a href="%s/dcmetadata/metadata/%d/edit/" target="_blank">Edit</a>' % (SERVER_APP_ROOT,self.id,SERVER_APP_ROOT,self.id)
		else:
			return '<a href="%s/dcmetadata/metadata/%d/edit/" target="_blank">Add</a>' % (SERVER_APP_ROOT,self.id)
	
	_get_metadata_link.allow_tags = True
	_get_metadata_link.short_description = "Metadata"
	
	
#	def _get_time_period(self):
#		'''
#		Return time period in the format (begin_year;end_year)
#		'''
#		begin_year = self.begin_year
#		end_year = self.end_year
#		if begin_year != None and end_year != None:
#			if begin_year <= end_year:
#				return '%d;%d' % (begin_year, end_year)
#			else:
#				return 'Invalid Time Period'
#		else:
#			return None
	
	
	class Meta:
		db_table = u'source_data_inventory'

# Add Table Tags to TableMetadata After SourceDataInventory Model instance being saved
post_save.connect(post_save_handler_add_tabletags, sender=SourceDataInventory)

# Dataset Metadata Model
class DatasetMetadata(models.Model):
	id = models.IntegerField(primary_key=True)
	metadata = models.TextField(verbose_name='Original Dataset Metadata in JSON')
	
	def _get_metadata_dict(self):
		'''
		Return a dictionary of metadata elements from JSON field
		JSON Format:
		{
			"name":"dataset name",
			"tables":[core table, related tables],
			"fields":["table_name.field_name"]
		}
		'''
		if self.metadata != "":
			metadata_dict = json.loads(self.metadata)
		else:
			metadata_dict = None
		return metadata_dict
	
	_get_metadata_dict.short_descripton = "Metadata Dictionary"
	
	def __unicode__(self):
		return self.id	

	class Meta:
		db_table = u'dataset_metadata'


# Table Metadata Model
class TableMetadata(models.Model):
	id = models.IntegerField(primary_key=True)
	metadata = models.TextField(verbose_name='Original Table Metadata in JSON')
	
	def _get_metadata_dict(self):
		'''
		Return a dictionary of metadata elements from JSON field
		JSON Format:
		{
			"table_tags":{
					"title":"title",
					"geography":"geographic extent/coverage",
					"geographic_level":"geographical unit",
					"domain":"macro domain/topic",
					"subdomain":"subdomain/subject",
					"source":"source",
					"year":"YYYY",
					"geometry":"spatial_table_id",
					"description":"description",
					"data_consideration":"data_consideration"
					#"time_period":"begin_year;end_year"
				},
			"field_metadata":[
				{
					"field_name":"field name",
					"data_type":"data type",
					"verbose_name":"human-readable field name",
					"no_data_value":"no data value",
					"tags":
					{
						"geography":"geographic extent/coverage",
						"geographic_level":"geographical unit",
						"domain":"macro domain/topic",
						"subdomain":"subdomain/subject",
						year":"YYYY",
						#"time_period":"begin_year;end_year",
						"visualization_types":["visualization type"],
						"geometry":"spatial_table_id"
					}
				}
			]
		}
		'''		
		if self.metadata != "":
			metadata_dict = json.loads(self.metadata)
		else:
			metadata_dict = None
		return metadata_dict
	
	_get_metadata_dict.short_descripton = "Metadata Dictionary"
	
	def __unicode__(self):
		return self.id	

	class Meta:
		db_table = u'table_metadata'
	
# This metadata model is for XML metadata collection and has been abandoned.
## Metadata Model
#class Metadata(models.Model):
#	metadata = models.TextField(verbose_name='Original Metadata in XML')
#	metadata_json = models.TextField(verbose_name='Original Metadata in JSON')
#	
##	def _get_metadata_string(self):
##		'''
##		Return list of fields from metadata field as a stirng
##		'''
##		fields = []
##		tree = ElementTree.ElementTree(ElementTree.fromstring(self.metadata))
##		root = tree.getroot()
##		for child in root:
##			for child1 in child:
##				for (counter,child2) in enumerate(child1):
##					tag = child2.tag
##					data = child2.text
##					field =  tag + ":" + data + ("; " if counter == 2 else ", ")
##					# regular expressin to remove control characters (\n \r \t) from xml
##					fields.append(re.sub(r'[\t\n]','',field)) 
##		metadata_fields = ''.join(fields)
##		return metadata_fields
##	
##	_get_metadata_string.short_description = "Metadata"
#	
#	def _get_metadata_dict(self):
#		'''
#		Return a dictionary list of metadata elements
#		'''
#		metadata_dict_list = []
#		field_dict_list = []
#		other_dict_list = []
#		tree = ElementTree.ElementTree(ElementTree.fromstring(self.metadata))
#		root = tree.getroot()
#		# get the tag-value pair for metadata fields
#		for field in root[0]:
#			field_dict_list.append({field[0].tag:re.sub(r'[\t\n\r]','',field[0].text),
#									field[1].tag:re.sub(r'[\t\n\r]','',field[1].text) if field[1].text != None else '',
#									field[2].tag:re.sub(r'[\t\n\r]','',field[2].text) if field[2].text != None else '',
#									field[3].tag:re.sub(r'[\t\n\r]','',field[3].text) if field[3].text != None else '',}
#									)# regular expressin to remove control characters (\n \r \t) from xml
#		metadata_dict_list.append(field_dict_list)
#		# get the tag-value pair for other metadata information
#		for other in root[1]:
#			other_dict_list.append({other[0].tag:re.sub(r'[\t\n\r]','',other[0].text) if other[0].text != None else '',
#									other[1].tag:re.sub(r'[\t\n\r]','',other[1].text) if other[1].text != None else ''}
#									)# regular expressin to remove control characters (\n \r \t) from xml
#		metadata_dict_list.append(other_dict_list)
#
#		return metadata_dict_list
#	
#	_get_metadata_dict.short_description = "Metadata Dictionary List"
#	
#	def _get_metadata_json_dict(self):
#		'''
#		Return a dictionary of metadata elements from JSON field
#		JSON Format:
#		{
#			"table_tags":{
#					"geography":"geographic extent/coverage",
#					"geographic_level":"geographical unit",
#					"domain":"macro domain/topic",
#					"subdomain":"subdomain/subject",
#					"source":"source",
#					"time_period":"begin_year;end_year"
#				},
#			"field_metadata":[
#				{
#					"field_name":"field name",
#					"data_type":"data type",
#					"verbose_name":"human-readable field name",
#					"no_data_value":"no data value",
#					"tags":
#					{
#						"geography":"geographic extent/coverage",
#						"geographic_level":"geographical unit",
#						"domain":"macro domain/topic",
#						"subdomain":"subdomain/subject",
#						"time_period":"begin_year;end_year",
#						"visualization_types":["visualization type"],
#						"geometry":"spatial_table_id"
#					}
#				}
#			]
#		}
#		'''
#		if self.metadata_json != "":
#			metadata_dict = json.loads(self.metadata_json)
#		else:
#			metadata_dict = None
#		return metadata_dict
#	
#	_get_metadata_json_dict.short_descripton = "Metadata JSON Dictionary"
#
#	
#	def __unicode__(self):
#		return self.id	
#	
#	class Meta:
#		db_table = u'metadata'