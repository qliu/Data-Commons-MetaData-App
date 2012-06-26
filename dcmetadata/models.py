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
		
	class Meta:
		db_table = u'source_data_inventory'
		
	_get_file_size.short_description = "File Size"
	

# Metadata Model
class Metadata(models.Model):
	metadata = models.TextField(verbose_name='Original Metadata in XML')
	
	def _get_metadata(self):
		'''
		Return list of fields from metadata field
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
	
	_get_metadata.short_description = "Metadata"
	
	class Meta:
		db_table = u'test'