from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django import forms
from ptp.models import Jobs
from subprocess import Popen
import os

class GMYCForm(forms.Form):
    treefile = forms.FileField(label='My ultrametric input tree:')
    #rooted = forms.ChoiceField(choices = (("untrooted", "Unrooted"), ("rooted", "Rooted")), label = 'My tree is:')
    pvalue = forms.DecimalField(label = 'P-value:', initial = 0.01)
    #sender = forms.EmailField(label='My e-mail address:')

def index(request):
    context = {}
    return render(request, 'index.html', context)

def thanks(request):
    return HttpResponse("Thanks for using our service!")

def gmyc_index(request):
    if request.method == 'POST': # If the form has been submitted...
        gmyc_form = GMYCForm(request.POST, request.FILES) # A form bound to the POST data
        if gmyc_form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            job = Jobs()
            #job.email = ptp_form.cleaned_data['sender']
            job.email = "noemail@noemail.com"
            job.data_type = "umtree"
            job.method = "GMYC"
            job.save()
            filepath = settings.MEDIA_ROOT + repr(job.id) + "/" 
            os.mkdir(filepath)
            newfilename = filepath + "input.tre"
            handle_uploaded_file(fin = request.FILES['treefile'] , fout = newfilename)
            job.filepath = filepath
            job.save()
            pvalue = gmyc_form.cleaned_data['pvalue']
            os.chmod(filepath, 0777)
            
            run_gmyc(fin = newfilename, fout = filepath + "output.txt", pv = pvalue)
            
            #return HttpResponseRedirect('result/') # Redirect after POST
            return show_gmyc_result(request, job_id = repr(job.id))
    else:
        gmyc_form = GMYCForm() # An unbound form
    context = {'pform':gmyc_form}
    return render(request, 'gmyc/index.html', context)

def show_gmyc_result(request, job_id):
    out_path = settings.MEDIA_ROOT + job_id + "/output.txt"
    with open(out_path) as outfile:
        lines = outfile.readlines()
        if len(lines) > 5:
            results="<br>".join(lines)
            context = {'result':results, 'jobid':job_id}
            return render(request, 'gmyc/results.html', context)
        else:
            return render(request, 'gmyc/results.html', {'result':"Job still running", 'jobid':job_id})
     

def handle_uploaded_file(fin, fout):
    with open(fout, 'w+') as destination:
        for chunk in fin.chunks():
            destination.write(chunk)
            
def run_gmyc(fin, fout, pv = 0.01):
	#GMYC.py -t example/gmyc_example.tre -ps
    Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/GMYC.py", "-t", fin, "-pvalue", str(pv), "-ps"], stdout=open(fout, "w"), stderr=open(fout+".err", "w") )
    
