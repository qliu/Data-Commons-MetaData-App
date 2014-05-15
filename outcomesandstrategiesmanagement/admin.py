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
    fields = ['name']
    list_display = ('id','name')
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
    list_display = ('_get_str_id','description','outcome_20_name')
    list_filter = ['outcome_20']
    search_fields = ['description']
    list_per_page = 15
admin.site.register(Outcome10to19,Outcome10to19Admin)
    
class ThreeYearGoalAdmin(admin.ModelAdmin):
    fields = ['description','outcome_20','outcome_10_19']
    list_display = ('_get_str_id','description','outcome_10_19_name','outcome_20_name')
    list_filter = ['outcome_20','outcome_10_19']
    list_per_page = 15
    
    def outcome_10_19_name(self,obj):
        return obj.outcome_10_19.description
    outcome_10_19_name.short_description = "10-19 Year Outcome"
    
    def outcome_20_name(self,obj):
        return obj.outcome_10_19.outcome_20.description
    outcome_20_name.short_description = "20 Year Outcome"
admin.site.register(ThreeYearGoal,ThreeYearGoalAdmin)

class StrategyAdmin(admin.ModelAdmin):
    fields = ['id','str_id','description','rationale','outcome_20','outcome_10_19','three_year_goal','last_edit']
    readonly_fields = ['id','str_id','last_edit']
    list_display = ('_get_str_id','description','three_year_goal_name','outcome_10_19_name')
    list_filter = ['outcome_20','outcome_10_19','three_year_goal']
    search_fields = ['description','rationale']
    list_per_page = 15
    
    def outcome_10_19_name(self,obj):
        return obj.three_year_goal.outcome_10_19.description
    outcome_10_19_name.short_description = "10-19 Year Outcome"
    
    def three_year_goal_name(self,obj):
        return obj.three_year_goal.description
    three_year_goal_name.short_description = "3-Year Goal"
admin.site.register(Strategy,StrategyAdmin) 

class ActivityAdmin(admin.ModelAdmin):
    fields = ['id','description','rationale','strategy','last_edit']
    readonly_fields = ['id','last_edit']
    list_display = ('id','description','strategy_id','entity')
    list_filter = ['strategy__outcome_20','strategy__outcome_10_19','strategy__three_year_goal','strategy__str_id','entity','budget__capital_type','budget__fiscal_year']
    search_field = ['description','rationale']
    list_per_page = 15
    
    def strategy_id(self,obj):
        return obj.strategy.str_id
    strategy_id.short_description = "Strategy ID"
admin.site.register(Activity,ActivityAdmin)

class BudgetAdmin(admin.ModelAdmin):
    fields = ['id','activity','capital_type','fiscal_year','amount']
    readonly_fields = ['id']
    list_display = ('id','activity','amount','capital_type','fiscal_year')
    list_filter = ['capital_type__name','fiscal_year__name']
    search_field = ['activity__name']
    list_per_page = 15
    
    def add_view(self,request,form_url='',extra_context=None):
        activity_id = request.GET.get("activity",None)
        if activity_id != None:
            activity = Activity.objects.get(id=activity_id)
            data = request.GET.copy()
            data.update({
                'activity_id':activity_id
            })
            request.GET = data
        return super(BudgetAdmin,self).add_view(request,form_url,extra_context)    
admin.site.register(Budget,BudgetAdmin)