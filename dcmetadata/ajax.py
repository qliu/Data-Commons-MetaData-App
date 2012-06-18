from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

@dajaxice_register
def test_dajaxice_function(request):
    return simplejson.dumps({'message':'Hello World'})