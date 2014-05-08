from outcomesandstrategiesmanagement.models import *
from outcomesandstrategiesmanagement.forms import *
from django.contrib import admin

# Import from general utilities
from util import *

#===========================================
# Customized Admin for Look-up table models
#===========================================
class EntityAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 15
admin.site.register(Entity,EntityAdmin)
    
class CapitalTypeAdmin(admin.ModelAdmin):
    fields = ['name','entity']
    list_display = ('id','name','entity')
    list_per_page = 15
admin.site.register(CapitalType,CapitalTypeAdmin)
    
class FiscalYearAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('id','name')
    list_per_page = 15
admin.site.register(FiscalYear,FiscalYearAdmin)

#===========================================
# Customized Admin for Data Models
#===========================================
class Outcome20Admin(admin.ModelAdmin):
    fields = ['description']
    list_display = ('id','description')
    list_per_page =  15
admin.site.register(Outcome20,Outcome20Admin)
    
class Outcome10to19Admin(admin.ModelAdmin):
    fields = ['description','outcome_20']
    list_display = ('id','_get_str_id','description','outcome_20')
    list_filter = ['outcome_20']
    search_fields = ['description']
    list_per_page = 15
admin.site.register(Outcome10to19,Outcome10to19Admin)
    
class ThreeYearGoalAdmin(admin.ModelAdmin):
    fields = ['description','outcome_20','outcome_10_19']
    list_display = ('id','_get_str_id','description','outcome_10_19')
    list_filter = ['outcome_20','outcome_10_19']
    list_per_page = 15
admin.site.register(ThreeYearGoal,ThreeYearGoalAdmin)

class StrategyAdmin(admin.ModelAdmin):
    fields = ['id','description','rationale','outcome_20','outcome_10_19','three_year_goal','last_edit']
    readonly_fields = ['id','last_edit']
    list_display = ('_get_str_id','description','three_year_goal')
    list_filter = ['outcome_20','outcome_10_19','three_year_goal']
    search_fields = ['description','rationale']
    list_per_page = 15
admin.site.register(Strategy,StrategyAdmin)

class ActivityAdmin(admin.ModelAdmin):
    fields = ['id','description','rationale','strategy','last_edit']
    readonly_fields = ['id','last_edit']
    list_display = ('description','rationale','strategy','last_edit')
    list_filter = ['strategy__outcome_20','strategy__outcome_10_19','strategy__three_year_goal','strategy']
    search_field = ['description','rationale']
    list_per_page = 15
admin.site.register(Activity,ActivityAdmin)

class BudgetAdmin(admin.ModelAdmin):
    fields = ['id','activity','capital_type','fiscal_year','amount']
    readonly_fields = ['id']
    list_display = ('id','activity','amount','capital_type','fiscal_year')
    list_filter = ['activity','capital_type','fiscal_year']
    search_field = ['activity__name']
    list_per_page = 15
admin.site.register(Budget,BudgetAdmin)