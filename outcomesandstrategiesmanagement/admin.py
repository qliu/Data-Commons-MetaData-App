from outcomesandstrategiesmanagement.models import *
from outcomesandstrategiesmanagement.forms import *
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse

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
    list_display = ('_get_str_id','description','_outcome_20_name')
    list_display_field_names = ('id','Description','20 Year Outcome')# Custom admin attr as headers for export
    list_filter = ['outcome_20']
    search_fields = ['description']
    list_per_page = 15
admin.site.register(Outcome10to19,Outcome10to19Admin)

class ThreeYearGoalAdmin(admin.ModelAdmin):
    fields = ['description','outcome_20','outcome_10_19']
    list_display = ('_get_str_id','description','_outcome_10_19_name','_outcome_20_name')
    list_display_field_names = ('id','Description','10-19 Year Outcome','20 Year Outcome')# Custom admin attr as headers for export
    list_filter = ['outcome_20','outcome_10_19']
    list_per_page = 15
admin.site.register(ThreeYearGoal,ThreeYearGoalAdmin)

class StrategyAdmin(admin.ModelAdmin):
    fields = ['id','str_id','description','rationale','outcome_20','outcome_10_19','three_year_goal','last_edit']
    readonly_fields = ['id','str_id','last_edit']
    list_display = ('_get_str_id','description','_three_year_goal_name','_outcome_10_19_name')
    list_display_field_names = ('id','Description','3-Year Goal','10-19 Year Outcome')# Custom admin attr as headers for export
    list_filter = ['outcome_20','outcome_10_19','three_year_goal']
    search_fields = ['description','rationale']
    list_per_page = 15
admin.site.register(Strategy,StrategyAdmin) 

class ActivityLeadListFilter(SimpleListFilter):
    # Full name of Activity lead user
    title = "Lead"
    parameter_name = 'lead__id__exact'
    def lookups(self,request,model_admin):
        users = set([activity.lead for activity in model_admin.model.objects.all()])
        return([(user.id,"%s %s" % (user.first_name,user.last_name)) for user in users])

    def queryset(self,request,queryset):
        if self.value():
            return queryset.filter(lead__id__exact=self.value())
        else:
            return queryset

class ActivityAdmin(admin.ModelAdmin):
    fields = ['id','description','rationale','strategy','entity','status','lead','last_edit']
    readonly_fields = ['id','last_edit','lead']
    list_display = ('id','description','_strategy_id','entity','_get_lead_full_name','_get_total_budget')
    list_display_field_names = ('id','Description','Strategy ID','Entity','Lead','Total Budget')# Custom admin attr as headers for export
    list_filter = ['strategy__outcome_20','strategy__outcome_10_19','strategy__three_year_goal','strategy__str_id','entity','budget__capital_type','budget__fiscal_year',ActivityLeadListFilter]
    search_field = ['description','rationale']
    list_per_page = 15

#    form = ActivityAdminForm
    
    def save_model(self,request,obj,form,change):
        # when adding new activity, set lead to be logged in user by default
        if not change:
            obj.lead = request.user
        obj.save()
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
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()
    
        msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.
        if "_continue" in request.POST:
            print "continue"
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if "_popup" in request.POST:
                post_url_continue += "?_popup=1"
            return HttpResponseRedirect(post_url_continue % pk_value)
    
        if "_popup" in request.POST:
            print "popup"
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script></body></html>' % \
                # escape() calls force_unicode.
                (escape(pk_value), escapejs(obj)))
        elif "_addanother" in request.POST:
            print "add another"
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
            return HttpResponseRedirect(request.path+("?activity=%s" % obj.activity.id))
        else:
            print "else"
            self.message_user(request, msg)
    
            # Figure out where to redirect. If the user has change permission,
            # redirect to the change-list page for this object. Otherwise,
            # redirect to the admin index.
            if self.has_change_permission(request, None):
#                post_url = reverse('admin:%s_%s_changelist' %
#                                   (opts.app_label, opts.module_name),
#                                   current_app=self.admin_site.name)
                print "HHHHHHERE"
#                post_url = '../../activity/%s/' % obj.activity.id
                post_url = "%s/outcomesandstrategiesmanagement/activity/%s/budget_list/" % (APP_SERVER_URL,obj.activity.id)
            else:
                post_url = reverse('admin:index',
                                   current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)
    
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        opts = obj._meta
    
        # Handle proxy models automatically created by .only() or .defer().
        # Refs #14529
        verbose_name = opts.verbose_name
        module_name = opts.module_name
        if obj._deferred:
            opts_ = opts.proxy_for_model._meta
            verbose_name = opts_.verbose_name
            module_name = opts_.module_name
    
        pk_value = obj._get_pk_val()
    
        msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(verbose_name), 'obj': force_unicode(obj)}
        if "_continue" in request.POST:
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if "_popup" in request.REQUEST:
                return HttpResponseRedirect(request.path + "?_popup=1")
            else:
                return HttpResponseRedirect(request.path)
        elif "_saveasnew" in request.POST:
            msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % {'name': force_unicode(verbose_name), 'obj': obj}
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:%s_%s_change' %
                                        (opts.app_label, module_name),
                                        args=(pk_value,),
                                        current_app=self.admin_site.name))
        elif "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(verbose_name)))
#            return HttpResponseRedirect(reverse('admin:%s_%s_add' %
#                                        (opts.app_label, module_name),
#                                        current_app=self.admin_site.name))
            post_url = '../add/?activity=%s' % obj.activity.id
            return HttpResponseRedirect(post_url)
        else:
            self.message_user(request, msg)
            # Figure out where to redirect. If the user has change permission,
            # redirect to the change-list page for this object. Otherwise,
            # redirect to the admin index.
            if self.has_change_permission(request, None):
#                post_url = reverse('admin:%s_%s_changelist' %
#                                   (opts.app_label, module_name),
#                                   current_app=self.admin_site.name)
#                post_url = '../../activity/%s/' % obj.activity.id
                post_url = "%s/outcomesandstrategiesmanagement/activity/%s/budget_list/" % (APP_SERVER_URL,obj.activity.id)
            else:
                post_url = reverse('admin:index',
                                   current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)
    
admin.site.register(Budget,BudgetAdmin)