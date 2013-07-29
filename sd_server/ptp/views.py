from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django import forms
from models import Jobs
from subprocess import Popen
import os

class PTPForm(forms.Form):
    treefile = forms.FileField(label='My phylogenetic input tree:')
    rooted = forms.ChoiceField(choices = (("untrooted", "Unrooted"), ("rooted", "Rooted")), label = 'My tree is:')
    sender = forms.EmailField(label='My e-mail address:')

def index(request):
    context = {}
    return render(request, 'index.html', context)

def thanks(request):
    return HttpResponse("Thanks for using our service!")

def ptp_index(request):
    if request.method == 'POST': # If the form has been submitted...
        ptp_form = PTPForm(request.POST, request.FILES) # A form bound to the POST data
        if ptp_form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            job = Jobs()
            job.email = ptp_form.cleaned_data['sender']
            if ptp_form.cleaned_data['rooted'] == "rooted":
                job.data_type = "rptree"
            else:
                job.data_type = "ptree"
            job.method = "PTP"
            job.save()
            filepath = settings.MEDIA_ROOT + repr(job.id) + "/" 
            os.mkdir(filepath)
            newfilename = filepath + "input.tre"
            handle_uploaded_file(fin = request.FILES['treefile'] , fout = newfilename)
            job.filepath = filepath
            job.save()
            if ptp_form.cleaned_data['rooted'] == "rooted":
                run_ptp(fin = newfilename, fout = filepath + "output.txt", rooted = True)
            else:
                run_ptp(fin = newfilename, fout = filepath + "output.txt", rooted = False)
            
            #return HttpResponseRedirect('result/') # Redirect after POST
            return show_ptp_result(request, job_id = job.id, out_path = filepath + "output.txt")
    else:
        ptp_form = PTPForm() # An unbound form
    context = {'pform':ptp_form}
    return render(request, 'ptp/index.html', context)

def show_ptp_result(request, job_id, out_path = ""):
    with open(out_path) as outfile:
        lines = outfile.readlines()
        if len(lines) > 5:
            results="".join(lines[:-1])
            context = {'result':results}
            return render(request, 'ptp/results.html', context)
        else:
            return render(request, 'ptp/results.html', {'result':"Job still running"})
     

def handle_uploaded_file(fin, fout):
    with open(fout, 'w+') as destination:
        for chunk in fin.chunks():
            destination.write(chunk)
            
def run_ptp(fin, fout, rooted = False):
    if rooted:
        Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/PTP.py", "-t", fin, "-p"], stdout=open(fout, "w"))
    else:
        Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/PTP.py", "-t", fin, "-p", "-r"], stdout=open(fout, "w"))