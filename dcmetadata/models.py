from django.db import models
from django.contrib import admin
from django.core import serializers

# Import from general utilities
from util import *

# Choices
YEAR_CHOICES = tuple((i,i) for i in range (1980,2013))

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
		
## Subject Matter
class SubjectMatter(models.Model):
	'''
	Store subject of the source data
	'''	
#	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		db_table = u'inventory_subjectmatter'
		
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


# Source Data Inventory Model
class SourceDataInventory(models.Model):
	"""
	Inventory of the source data.
	"""	
#	id = models.IntegerField(primary_key=True)
	file_name = models.CharField(max_length=200, verbose_name='File Name')
	description = models.CharField(max_length=200, null=True, blank=True)
	macro_domain = models.ForeignKey('MacroDomain',verbose_name='Macro Domain')
	subject_matter = models.ForeignKey('SubjectMatter',verbose_name='Subject Matter')
	begin_year = models.IntegerField(verbose_name='Begin Year',choices=YEAR_CHOICES,null=True)
	end_year = models.IntegerField(verbose_name='End Year',choices=YEAR_CHOICES,null=True)
	geography = models.ForeignKey('Geography')
	coverage = models.ForeignKey('Coverage')
	source = models.ForeignKey('Source')
	format = models.ForeignKey('Format',null=True,blank=True)
	location =  models.CharField(max_length=200)
	file_size = models.FloatField(default=0,verbose_name='File Size',null=True, blank=True)
	metadata = models.ForeignKey('Metadata',null=True,blank=True)
	
	def __unicode__(self):
		'''
		Return file name as default for inventory entry
		'''
		return self.file_name
	
	def _get_year_range(self):
		'''
		Return year range from begin_year to end_year
		'''
		if self.begin_year != None and self.end_year != None:
			return '%d-%d' % (self.begin_year, self.end_year)
		else:
			return 'No Data'
		
	_get_year_range.short_description = "Dates"
	_get_year_range.admin_order_field = "begin_year"
	
	def is_within_year_range(self,year):
		'''
		Return True if year is within year range
		'''
		return self.begin_year <= year and year <= self.end_year
	
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
		try:
			metadata = Metadata.objects.get(id=self.id)
			return '<a href="%s/dcmetadata/metadata/%d/" target="_blank">View</a> <a href="%s/dcmetadata/metadata/%d/edit/" target="_blank">Edit</a>' % (SERVER_APP_ROOT,self.id,SERVER_APP_ROOT,self.id)
		except:
			return '<a href="%s/dcmetadata/metadata/%d/edit/" target="_blank">Add</a>' % (SERVER_APP_ROOT,self.id)
	
	_get_metadata_link.allow_tags = True
	_get_metadata_link.short_description = "Metadata"
	
	
	class Meta:
		db_table = u'source_data_inventory'


# Metadata Model
class Metadata(models.Model):
	metadata = models.TextField(verbose_name='Original Metadata in XML')
	
	def _get_metadata_string(self):
		'''
		Return list of fields from metadata field as a stirng
		'''
		fields = []
		tree = ElementTree.ElementTree(ElementTree.fromstring(self.metadata))
		root = tree.getroot()
		for child in root:
			for child1 in child:
				for (counter,child2) in enumerate(child1):
					tag = child2.tag
					data = child2.text
					field =  tag + ":" + data + ("; " if counter == 2 else ", ")
					# regular expressin to remove control characters (\n \r \t) from xml
					fields.append(re.sub(r'[\t\n]','',field)) 
		metadata_fields = ''.join(fields)
		return metadata_fields
	
	_get_metadata_string.short_description = "Metadata"
	
	def _get_metadata_dict(self):
		'''
		Return a dictionary list of metadata elements
		'''
		metadata_dict_list = []
		field_dict_list = []
		other_dict_list = []
		tree = ElementTree.ElementTree(ElementTree.fromstring(self.metadata))
		root = tree.getroot()
		# get the tag-value pair for metadata fields
		for field in root[0]:
			field_dict_list.append({field[0].tag:re.sub(r'[\t\n\r]','',field[0].text),
									field[1].tag:re.sub(r'[\t\n\r]','',field[1].text) if field[1].text != None else '',
									field[2].tag:re.sub(r'[\t\n\r]','',field[2].text) if field[2].text != None else '',
									field[3].tag:re.sub(r'[\t\n\r]','',field[3].text) if field[3].text != None else '',}
									)# regular expressin to remove control characters (\n \r \t) from xml
		metadata_dict_list.append(field_dict_list)
		# get the tag-value pair for other metadata information
		for other in root[1]:
			other_dict_list.append({other[0].tag:re.sub(r'[\t\n\r]','',other[0].text) if other[0].text != None else '',
									other[1].tag:re.sub(r'[\t\n\r]','',other[1].text) if other[1].text != None else ''}
									)# regular expressin to remove control characters (\n \r \t) from xml
		metadata_dict_list.append(other_dict_list)

		return metadata_dict_list
	
	_get_metadata_dict.short_description = "Metadata Dictionary List"
	
	def __unicode__(self):
		return self.id	
	
	class Meta:
		db_table = u'metadata'