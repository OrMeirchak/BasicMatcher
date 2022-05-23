from distutils.log import error
from django.conf import Settings
from django.shortcuts import render
from django.http import HttpResponse
from basicmatcher.engine import *
from basicmatcher.models import *

def index(request):
    return render(request,'index.html')

  
def matcher(request):
    input=request.GET['text']
    try:
      index=matcherEngine(input)
      if index is None:
          msg="No match found :("
      else:    
          res=Candidate.objects.filter(id=index).get()
          msg="Title:{} , skills: {} ".format(res.title,res.skills)
    except jobTitleDoesntExist:
        msg="Job title doesnt exists"

    

    
    return render(request,'matcher.html',{'msg':msg})
    
