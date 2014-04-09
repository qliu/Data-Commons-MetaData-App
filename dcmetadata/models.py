from django.db import models
from django.contrib import admin
from django.core import serializers
from django.db.models.signals import post_save,post_delete,m2m_changed
from django.core.mail import send_mail

# Import from general utilities
from util import *

# Choices
year_choices_list = [(None,"---------"),(0,"No Data")]
for i in range (1980,2013):
	year_choices_list.append((i,str(i)))
YEAR_CHOICES = tuple(year_choices_list)

BOOL_CHOICES = ((1,"Yes"),(0,"No"))

# Look-up tables:
## Macro Domain
class MacroDomain(models.Model):
	'''
	Store macro domain of the source data
	'''
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id	
	
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
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
	def __unicode__(self):
		return "%s | %s" % (self.macrodomain.name,self.name)
		
	class Meta:
		db_table = u'inventory_subjectmatter'
		ordering = ['macrodomain','name']
		
## Geography
class Geography(models.Model):
	'''
	Store geographic scale/level of the source data
	'''	
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
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
	geotable = models.ForeignKey('SpatialTable',verbose_name='Spatial Table')
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
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
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
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
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
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
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
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
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
	def __unicode__(self):
		return self.name

	class Meta:
		db_table = u'spatial_table'
		ordering = ['name']
		
# Tags Model
class Tag(models.Model):
	'''
	Store tags for dataset
	'''
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=100)
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		db_table = u'dataset_tag'
		ordering = ['name']

# Handler After SourceDataInventory Model instance being saved
def post_save_handler_add_tabletags(sender,instance=True,**kwargs):
	metadata_id = instance.id
	is_add_new_table = False
	data_status = ""
	
	# Save table name to DataTalbe lookup
	try:
		data_table = DataTable.objects.get(db_table=instance.file_name.lower())
		if data_table.table_name != instance.title:
			data_table.table_name = instance.title
			data_table.db_table = instance.file_name.lower()
			data_table.save()
		else:
			if data_table.db_table != instance.file_name.lower():
				data_table.db_table = instance.file_name.lower()
				data_table.save()
	except:
		data_table = DataTable(id=metadata_id,db_table=instance.file_name.lower(),table_name=instance.title)
		data_table.save()	
	
	if len(TableMetadata.objects.filter(id=metadata_id)) == 0:
		# If Add new table
		is_add_new_table = True
		json_field_metadata = []
	else:
		try:
			sourcedata = SourceDataInventory.objects.get(id=metadata_id)
			table_metadata = TableMetadata.objects.get(id=metadata_id)
			metadata_json = table_metadata.metadata
			metadata_json_dict = table_metadata._get_metadata_dict()
			json_field_metadata = metadata_json_dict["field_metadata"]
		except:
			pass;

	try:
		sourcedata = SourceDataInventory.objects.get(id=metadata_id)
	
		json_table_tags = {"title":instance.title,
						   "geography":instance.coverage.id,
						   "geographic_level":instance.geography.id,
						   "domain":instance.macro_domain.id,
						   "subdomain":instance.subject_matter.id,
						   "source":instance.source.id,
						   "source_website":instance.source_website,
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
		# Send admin email alert when source data added/changed
		email_content = {"subject":"[DataEngine_Metadata]",
						 "message":"",
						 "from": ADMIN_EMAIL_ADDRESS,
						 "to": TO_EMAIL_ADDRESS
						}
		if is_add_new_table:
			data_status = "Added"
		else:
			data_status = "Changed"
		email_content["subject"] += "%sSource Data %s - %s (id:%d)" % ("New " if is_add_new_table else "",data_status,instance.title, instance.id)
		email_content["message"] = 'This is a notification that %ssource data "%s" (id:%d) has been %s.' % ("new " if is_add_new_table else "",instance.title,instance.id,data_status)
		send_mail(email_content['subject'],email_content['message'],email_content['from'],email_content['to'])
	except:
		pass;
		
# Source Data Inventory Model
class SourceDataInventory(models.Model):
	"""
	Inventory of the source data.
	"""	
#	id = models.IntegerField(primary_key=True)
	file_name = models.CharField(max_length=200, verbose_name='File Name',null=True)
	title = models.CharField(max_length=200, null=True, blank=True)
	macro_domain = models.ForeignKey('MacroDomain',verbose_name='Domain',null=True)
	subject_matter = models.ForeignKey('SubjectMatter',verbose_name='Subdomain',null=True)
	year = models.IntegerField(verbose_name='Year',choices=YEAR_CHOICES,null=True)
	geography = models.ForeignKey('Geography',verbose_name='Geographic Level',null=True)
	coverage = models.ForeignKey('Coverage',verbose_name='Geography',null=True)
	source = models.ForeignKey('Source',null=True)
	source_website = models.URLField(max_length=5000,null=True,blank=True)
	format = models.ForeignKey('Format',null=True,blank=True)
	location =  models.CharField(max_length=200,null=True)
	file_size = models.FloatField(default=0,verbose_name='File Size',null=True, blank=True)
	metadata = models.ForeignKey('TableMetadata',null=True,blank=True)
	geometry = models.ForeignKey('SpatialTable',verbose_name='Spatial Table',null=True)
	description = models.CharField(max_length=500, null=True, blank=True)
	data_consideration = models.CharField(max_length=500, null=True, blank=True)
	process_notes = models.CharField(max_length=5000, null=True, blank=True)
	
	def __unicode__(self):
		'''
		Return file name as default for inventory entry
		'''
		return self.title
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if SourceDataInventory.objects.filter(id__lt=self.id):
			previous_id = SourceDataInventory.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if SourceDataInventory.objects.filter(id__gt=self.id):
			next_id = SourceDataInventory.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
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
			return '<a href="%s/dcmetadata/metadata/%d/" target="_blank">View</a> | <a href="%s/dcmetadata/metadata/%d/edit/" target="_blank">Edit</a>' % (SERVER_APP_ROOT,self.id,SERVER_APP_ROOT,self.id)
		else:
			return '<a href="%s/dcmetadata/metadata/%d/edit/" target="_blank">Add</a>' % (SERVER_APP_ROOT,self.id)
	
	_get_metadata_link.allow_tags = True
	_get_metadata_link.short_description = "Metadata"

	class Meta:
		db_table = u'source_data_inventory'
		ordering = ['title']

# Add Table Tags to TableMetadata After SourceDataInventory Model instance being saved
post_save.connect(post_save_handler_add_tabletags, sender=SourceDataInventory)

# Data Table Model
class DataTable(models.Model):
	id = models.IntegerField(primary_key=True)
	db_table = models.TextField(verbose_name='Database Table')
	table_name =  models.TextField(verbose_name='Table Name',null=True)
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
	def __unicode__(self):
		return u"%s" % self.id
	
	class Meta:
		db_table = u'data_tables'

# Table Metadata Model
class TableMetadata(models.Model):
	id = models.IntegerField(primary_key=True)
	metadata = models.TextField(verbose_name='Original Table Metadata in JSON')
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
	def _get_metadata_dict(self):
		'''
		Return a dictionary of metadata elements from JSON field
		JSON Format:
		{
			"table_tags":{
					"description":"title",
					"geography":"geographic extent/coverage",
					"geographic_level":"geographical unit",
					"domain":"macro domain/topic",
					"subdomain":"subdomain/subject",
					"source":"source",
					"source_website":"source websit URL",
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
						"year":"YYYY",
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
		return u"%s" % self.id	

	class Meta:
		db_table = u'table_metadata'

# Handler to respond the signal sent by Dataset.tags when Dataset Object is changed
# 	To update JSON metadata according to changes made to Dataset
# 	* The 'post_add' action and this handler are used
#	  because 'post_save' signal is sent by Dataset Object
#	  before the M2M fields 'tables' and 'tags' are saved in the database.
#	  Thus, 'm2m_changed' signal sent by M2M field 'tags' is used
#	  bacause 'tags' is the last M2M field which sends signals after Dataset is saved.
def post_save_m2m_tags_dataset(sender, instance, action, reverse, *args, **kwargs):
	if action == 'post_add' and not reverse:
		is_new_nid = False
		metadata_id = instance.id
		# Send admin email alert when source data added/changed
		email_content = {"subject":"[DataEngine_Metadata]",
						 "message":"",
						 "from": ADMIN_EMAIL_ADDRESS,
						 "to": TO_EMAIL_ADDRESS
						}	
		# If metadata not existed
		if len(DatasetMetadata.objects.filter(id=metadata_id)) == 0:
			json_metadata_dict = {}
			json_metadata = json.dumps(json_metadata_dict)
			output_metadata = DatasetMetadata(id=metadata_id,metadata=json_metadata)
			output_metadata.save()
			# Send email notification
			email_content["subject"] += "New Dataset Added - %s (id:%d)" % (instance.name, instance.id)
			email_content["message"] = 'This is a notification that new dataset "%s" (id:%d) has been added.' % (instance.name,instance.id)
			send_mail(email_content['subject'],email_content['message'],email_content['from'],email_content['to'])			
		else:
			# If dataset already existed, update metadata
			try:
				dataset = Dataset.objects.get(id=instance.id)
				dataset_metadata = DatasetMetadata.objects.get(id=metadata_id)
				metadata_json = dataset_metadata.metadata
				json_metadata_dict = dataset_metadata._get_metadata_dict()
				# If new node id assigned, send email notification of new dataset being added
				if instance.nid and instance.nid != json_metadata_dict["nid"]:
					is_new_nid = True
				json_metadata_dict["nid"] = instance.nid if instance.nid else ""
				json_metadata_dict["name"] = instance.name
				json_metadata_dict["tags"] = map(int,instance._get_str_tags().split(","))
				json_metadata_dict["large_dataset"] = instance.large_dataset
				# If tables changed, overwrite with new tables from instance, and reset all the fileds and keys values
				if not all(map(operator.eq,map(int,instance._get_str_tables().split(",")),json_metadata_dict["tables"])):
					json_metadata_dict["tables"] = map(int,instance._get_str_tables().split(","))			
					json_metadata_dict["fields"] = []
					json_metadata_dict["display_name"] = ""
					json_metadata_dict["pkey"] = []
					json_metadata_dict["fkeys"] = []
					json_metadata_dict["gkey"] = []
				json_metadata = json.dumps(json_metadata_dict)
				output_metadata = DatasetMetadata(id=metadata_id,metadata=json_metadata)
				output_metadata.save()
				# Send email notification
				if is_new_nid:
					email_content["subject"] += "New Dataset Added to DataEngine - %s (nid:%s)" % (instance.name, instance.nid)
					email_content["message"] = 'This is a notification that new dataset "%s" (nid:%s) has been imported to DataEngine. Click the link to view this dataset: http://codataengine.org/find/%s' % (instance.name,instance.nid,instance.name.strip().lower().replace(" by ","-").replace(" in ","-").replace("'","").replace("(","").replace(")","").replace(" ","-"))				
				else:
					email_content["subject"] += "Dataset Changed - %s (id:%d)" % (instance.name, instance.id)
					email_content["message"] = 'This is a notification that dataset "%s" (id:%d) has been changed.' % (instance.name,instance.id)
				email_content["to"] = TO_DE_ADMIN_EMAIL_ADDRESS
				send_mail(email_content['subject'],email_content['message'],email_content['from'],email_content['to'])			
			except:
				pass;		
	
# Delete Dataset Metadata after Dataset instance being deleted
def post_delete_handler_delete_datasetmetadata(sender,instance=True,**kwargs):
	metadata_id = instance.id
	try:
		dataset_metadata = DatasetMetadata.objects.get(id=metadata_id)
		dataset_metadata.delete()
	except:
		pass

# Dataset Model
class Dataset(models.Model):
	'''
	Dataset for DataEngine Application
	'''
	id = models.IntegerField(primary_key=True)
	nid = models.IntegerField(null=True,blank=True)
	name = models.CharField(max_length=500)
	tables = models.ManyToManyField('SourceDataInventory')
	tags = models.ManyToManyField('Tag',null=True,blank=True)
	large_dataset = models.IntegerField(choices=BOOL_CHOICES,default=0)
	metadata = models.ForeignKey('DatasetMetadata',null=True,blank=True)
	
	def __unicode__(self):
		'''
		Return dataset name as default
		'''
		return self.name
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
	
	def _get_str_tables(self):
		'''
		Display table ID list in comma-seperated string
		'''
		if self.tables.count() > 0:
			table_ids = []
			for table in self.tables.all():
				table_ids.append(table.id)
			txt_tables = ",".join(map(str,table_ids))
		else:
			txt_tables = ''
		return txt_tables
	
	_get_str_tables.short_description = "Tables"
	
	def _get_str_tags(self):
		'''
		Display tag ID list in comma-seperated string
		'''
		if self.tags.count() > 0:
			tag_ids = []
			for tag in self.tags.all():
				tag_ids.append(tag.id)
			txt_tags = ",".join(map(str,tag_ids))
		else:
			txt_tags = ''
		return txt_tags
	
	_get_str_tags.short_description = "Tags"
	
	def _is_large_dataset(self):
		'''
		Return Yes or No for Large_dataset flag
		'''
		if self.large_dataset == 1:
			is_large_dataset = 'Yes'
		elif self.large_dataset == 0:
			is_large_dataset = 'No'
		else:
			is_large_dataset = ''
		return is_large_dataset
	
	_is_large_dataset.short_description = "Is Large Dataset?"
	
	def _get_metadata_link(self):
		'''
		Return HTML link for view and edit metadata associated with record
		'''
		if self.metadata != None:
			return '<a href="%s/dcmetadata/dataset/metadata/%d/" target="_blank">View</a> | <a href="%s/dcmetadata/dataset/metadata/%d/edit/" target="_blank">Edit</a>' % (SERVER_APP_ROOT,self.id,SERVER_APP_ROOT,self.id)
		else:
			return '<a href="%s/dcmetadata/dataset/metadata/%d/edit/" target="_blank">Add</a>' % (SERVER_APP_ROOT,self.id)	
	
	_get_metadata_link.short_description = "Metadata"
	_get_metadata_link.allow_tags = True	
	
	class Meta:
		db_table = u'dataset'
		ordering = ['name']

# Add tags after Dataset M2M field tags being changed
m2m_changed.connect(post_save_m2m_tags_dataset,sender=Dataset.tags.through)

# Delete Dataset Metadata after Dataset Model instance being deleted
post_delete.connect(post_delete_handler_delete_datasetmetadata, sender=Dataset)

# Dataset Metadata Model
class DatasetMetadata(models.Model):
	id = models.IntegerField(primary_key=True)
	metadata = models.TextField(verbose_name='Original Dataset Metadata in JSON')
	
	def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__lt=self.id):
			previous_id = Dataset.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
	
	def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Dataset.objects.filter(id__gt=self.id):
			next_id = Dataset.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id	
	
	def _get_metadata_dict(self):
		'''
		Return a dictionary of metadata elements from JSON field
		JSON Format:
		{
			"nid":"node id",
			"name":"dataset name",
			"tables":[core table id, related table ids],
			"fields":["table_id.field_name"],
			"display_name":"table_id.field_name",
			"pkey":["table_id.field_name"],
			"fkeys":[["table_id.field_name","reference_table_id.field_name"]],
			"gkey":["table_id.field_name","spatial_table_id.field_name"],
			"tags":[tag ids],
			"large_dataset":1/0
		}
		'''
		if self.metadata != "":
			metadata_dict = json.loads(self.metadata)
		else:
			metadata_dict = None
		return metadata_dict
	
	_get_metadata_dict.short_descripton = "Metadata Dictionary"
	
	def __unicode__(self):
		return u"%s" % self.id	

	class Meta:
		db_table = u'dataset_metadata'

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