from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django import forms
from ptp.models import Jobs
from subprocess import Popen
import os

class GMYCForm(forms.Form):
    treefile = forms.FileField(label='My ultrametric input tree (Newick format only):')
    method = forms.ChoiceField(choices = (("single", "Single threshold"), ("multi", "Multi threshold")), label = 'Method:')
    #pvalue = forms.DecimalField(label = 'P-value:', initial = 0.01)
    sender = forms.EmailField(label='My e-mail address:')


def index(request):
    context = {}
    return render(request, 'index.html', context)


def thanks(request):
    return HttpResponse("Thanks for using our service!")


def autherror(request):
    return HttpResponse("Job id does not exists or e-mail address does not match!")


def gmyc_index(request):
    if request.method == 'POST': # If the form has been submitted...
        gmyc_form = GMYCForm(request.POST, request.FILES) # A form bound to the POST data
        if gmyc_form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            job = Jobs()
            job.email = gmyc_form.cleaned_data['sender']
            job.data_type = "umtree"
            job.method = "GMYC"
            job.save()
            filepath = settings.MEDIA_ROOT + repr(job.id) + "/" 
            os.mkdir(filepath)
            newfilename = filepath + "input.tre"
            handle_uploaded_file(fin = request.FILES['treefile'] , fout = newfilename)
            job.filepath = filepath
            job.save()
            #pvalue = gmyc_form.cleaned_data['pvalue']
            #os.chmod(filepath, 0777)
            
            if gmyc_form.cleaned_data['method'] == "single":
                mode = "s"
            else:
                mode = "m"
            
            run_gmyc(fin = newfilename, fout = filepath + "output", mode = mode)
            
            return show_gmyc_result(request, job_id = repr(job.id), email = job.email)
    else:
        gmyc_form = GMYCForm() # An unbound form
    context = {'pform':gmyc_form}
    return render(request, 'gmyc/index.html', context)


def show_gmyc_result(request, job_id = "", email = ""):
    if job_id == "" or email == "":
        job_id = request.GET.get('job_id', '')
        email = request.GET.get('email', '')
    
    jobs = Jobs.objects.filter(id=job_id)
    if len(jobs) > 0:
        if jobs[0].email != email:
            return autherror(request)
    else:
        return autherror(request)
    
    out_path = settings.MEDIA_ROOT + job_id + "/input.tre_summary"
    screenout = settings.MEDIA_ROOT + job_id + "/output"
    err = settings.MEDIA_ROOT + job_id + "/output.err"
    plot = settings.MEDIA_ROOT + job_id +"/input.tre_plot.png"
    
    if os.path.exists(out_path) and os.path.exists(plot):
        with open(out_path) as outfile:
            lines = outfile.readlines()
            results="<br>".join(lines)
            context = {'result':results, 'jobid':job_id}
            return render(request, 'gmyc/results.html', context)
    else:
        with open(err) as ferr:
            lines = ferr.readlines()
            if len(lines) > 5:
                return render(request, 'gmyc/results.html', {'result':"Something is wrong, please check your input file", 'jobid':job_id, 'email':email})
            else:
                return render(request, 'gmyc/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email})


def handle_uploaded_file(fin, fout):
    with open(fout, 'wb+') as destination:
        for chunk in fin.chunks():
            destination.write(chunk)


def run_gmyc(fin, fout, mode = "s"):
    #GMYC.py -t example/gmyc_example.tre -ps
    #Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/GMYC.py", "-t", fin, "-pvalue", str(pv), "-ps"], stdout=open(fout, "w"), stderr=open(fout+".err", "w") )
    Popen(["nohup", settings.MEDIA_ROOT + "bin" + "/gmyc.script.R", fin, mode], stdout=open(fout, "w"), stderr=open(fout+".err", "w") )

