from django.core.urlresolvers import resolve
from datacommons.settings import SERVER_URL,APP_SERVER_URL

def appname(request):
    url = request.path
    url = url.replace(SERVER_URL,"").replace(APP_SERVER_URL,"")
    if url.startswith("/admin/"):
        app_name = url.partition("/admin/")[2].partition("/")[0]
    elif url.startswith("/login/"):
        if "next" in request.GET:
            app_name = request.GET["next"].replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
        else:
            url = request.META["HTTP_REFERER"]
            if url.partition("/?next=/")[1] == "":
                app_name = url.partition("http://")[2].partition("/")[2].partition("/")[0]
            else:
                app_name = url.partition("/?next=/")[2].partition("/")[0]        
    elif url.startswith("/register/"):
        url=request.META["HTTP_REFERER"].partition("/?next=/")[2]
        if APP_SERVER_URL == "":
            # a trick for localhost
            app_name = url.replace(APP_SERVER_URL,"").partition("/")[0]
        else:
            app_name = url.replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
    else:
        app_name = url.partition("/")[2].partition("/")[0]
    return {'appname':app_name}