from django.db import models
from django.contrib import admin
from django.core import serializers
from django.db.models.signals import post_save,post_delete,m2m_changed
from django.core.mail import send_mail

# Import from general utilities
from util import *

#=================
# Look-up tables
#=================
class Entity(models.Model):
    """
    Store entity for capital type
    """
#    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'entity'

class CapitalType(models.Model):
    """
    Store capital type for Activity Budge
    """
#    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    entity = models.ForeignKey('Entity')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'capital_type'
        ordering = ['name']
        
class FiscalYear(models.Model):
    """
    Store Fiscal Year for Activity Budget
    """
#    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'fiscal_year'
        ordering = ['name']

# =============
# Model Tables
# =============
# 20- Year Outcome Model
class Outcome20(models.Model):
    """
    20- Year Outcomes
    """
#    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    
    def __unicode__(self):
        '''
        Return description as default for 20- year outcome entry
        '''
        return "20-Year Outcome #%d: %s" % (self.id,self.description)
    
    class Meta:
        db_table = u'outcome_20'
        ordering = ['id']

# 10-19 Year Outcome Model
class Outcome10to19(models.Model):
    """
    10-19 Year Outcomes
    """
#    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    outcome_20 = models.ForeignKey('Outcome20',verbose_name='20- Year Outcome')
    
    def __unicode__(self):
        '''
        Return description as default for 10-19 year outcome entry
        '''
        return "Outcome #%d | %s" % (self.outcome_20.id,self.description)
    
    def _get_str_id(self):
        '''
        Return the ID string of 10-19 Year Outcome according to the naming convention:
            Outcome#.10-19YrGoal#
            e.g. "O1.1"
                stands for Outcome#1.10-19YearGoal#1
        '''
        outcome_20_id = self.outcome_20.id
        outcomes = Outcome10to19.objects.filter(outcome_20=self.outcome_20)
        outcome_ids = []
        for outcome in outcomes:
            outcome_ids.append(outcome.id)
        outcome_ids.sort()
        outcome_10_19_id = outcome_ids.index(self.id)+1 
        return "O%d.%d" % (outcome_20_id,outcome_10_19_id)
    _get_str_id.short_description = "10-19 Year Outcome ID"    
    
    class Meta:
        db_table = u'outcome_10_19'
        ordering = ['outcome_20','id']

# ThreeYearGoal Model
class ThreeYearGoal(models.Model):
    """
    3 Year Goal
    """
#    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    outcome_20 = models.ForeignKey('Outcome20',verbose_name='20-Year Outcome')
    outcome_10_19 = models.ForeignKey('Outcome10to19',verbose_name='10-19 Year Outcome')
    
    def __unicode__(self):
        '''
        Return description as default for 3-year goal entry
        '''
        return "%s %s" % (self._get_str_id(),self.description)
    
    def _get_str_id(self):
        '''
        Return the ID string of strategy according to the naming convention:
            Outcome#.10-19YrGoal#.3YrGoal
            e.g. "O1.1.1"
                stands for Outcome#1.10-19YearGoal#1.3YearGoal#1
        '''
        goals = ThreeYearGoal.objects.filter(outcome_10_19=self.outcome_10_19)
        goal_ids = []
        for goal in goals:
            goal_ids.append(goal.id)
        goal_ids.sort()
        threeyeargoal_id = goal_ids.index(self.id)+1
        return "%s.%d" % (self.outcome_10_19._get_str_id(),threeyeargoal_id)
    _get_str_id.short_description = "3-Year Goal ID"    
    
    class Meta:
        db_table = u'three_year_goal'
        ordering = ['outcome_20','outcome_10_19','id']        
        

# Strategy Model
class Strategy(models.Model):
    """
    Strategies
    """
#    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=500,null=True,blank=True)
    rationale = models.CharField(max_length=1000,null=True,blank=True)
    outcome_20 = models.ForeignKey('Outcome20',verbose_name='20-Year Outcome')
    outcome_10_19 = models.ForeignKey('Outcome10to19',verbose_name='10-19 Year Outcome')
    three_year_goal = models.ForeignKey('ThreeYearGoal',verbose_name='3 Year Goal')
    last_edit = models.DateTimeField(auto_now_add=True,auto_now=True)
    is_active = models.BooleanField(default=True)
        
    def __unicode__(self):
		'''
		Return description as default for strategy entry
		'''
		return "%s. %s" % (self._get_str_id(),self.description)
            
    def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Strategy.objects.filter(id__lt=self.id):
			previous_id = Strategy.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
            
    def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Strategy.objects.filter(id__gt=self.id):
			next_id = Strategy.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
    
    def _get_str_id(self):
        '''
        Return the ID string of strategy according to the naming convention:
            Outcome#.10-19YrGoal#.3YrGoal#Strategy#
            e.g. "O1.1.1a"
                stands for Outcome#1.10-19YearGoal#1.3YearGoal#1 Strategy a
        '''
        strategies = Strategy.objects.filter(three_year_goal=self.three_year_goal)
        strategy_ids = []
        for strategy in strategies:
            strategy_ids.append(strategy.id)
        strategy_ids.sort()
        strategy_id = strategy_ids.index(self.id)+1
        strategy_id_chr = chr(strategy_id+ord("a")-1)
        return "%s%c" % (self.three_year_goal._get_str_id(),strategy_id_chr)
    _get_str_id.short_description = "Strategy ID"
            
    class Meta:
		db_table = u'strategy'
		ordering = ['outcome_20','outcome_10_19','three_year_goal','id']

# Activity Model
class Activity(models.Model):
    """
    Activities
    """
#    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    rationale = models.CharField(max_length=1000, null=True, blank=True)
    strategy = models.ForeignKey('Strategy',verbose_name='Strategy')
#    budgets = models.ManyToManyField('Budget',null=True,blank=True)
    last_edit = models.DateTimeField(auto_now_add=True,auto_now=True)
    is_active = models.BooleanField(default=True)
        
    def __unicode__(self):
		'''
		Return description as default for activity entry
		'''
		return self.description
            
    def get_previous_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Activity.objects.filter(id__lt=self.id):
			previous_id = Activity.objects.filter(id__lt=self.id).order_by('-id')[0].id
		else:
			previous_id = -1
		return previous_id
            
    def get_next_record_id(self):
		'''
		Return the ID of previous record in the table
		'''
		if Activity.objects.filter(id__gt=self.id):
			next_id = Activity.objects.filter(id__gt=self.id).order_by('id')[0].id
		else:
			next_id = -1
		return next_id
            
    class Meta:
		db_table = u'activity'
		ordering = ['strategy','description']

# Budget Model
class Budget(models.Model):
    """
    Budgets
    """
#    id = models.IntegerField(primary_key=True)
    activity = models.ForeignKey('Activity',verbose_name='Activity')
    capital_type = models.ForeignKey('CapitalType',verbose_name='Capital Type')
    fiscal_year = models.ForeignKey('FiscalYear',verbose_name='Fiscal Year')
    amount = models.FloatField(default=0,null=True, blank=True)
    
    def __unicode__(self):
        return self.amount
    
    class Meta:
        db_table = u'budget'
        ordering = ['fiscal_year']