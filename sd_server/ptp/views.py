from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django import forms
from models import Jobs
from subprocess import Popen
from subprocess import call
import subprocess
import os

class PTPForm(forms.Form):
    treefile = forms.FileField(label="""My phylogenetic input tree, 
    if input file contains multiple trees, only the first tree will be used:""")
    rooted = forms.ChoiceField(choices = (("untrooted", "Unrooted"), ("rooted", "Rooted")), label = 'My tree is:',
                                help_text = "If unrooted, the tree will be rooted at the longest branch.")
    #pvalue = forms.DecimalField(label = 'P-value:', initial = 0.001)
    nmcmc = forms.IntegerField(label = "No. MCMC generations:", initial = 100000, max_value = 500000, min_value = 10000,
                                help_text = """For small trees (<50 taxa), 100000 is usually enough, but you should always check for convergence.""")
    imcmc = forms.IntegerField(label = "Thinning:", initial = 100, max_value = 1000, min_value = 100)
    burnin = forms.DecimalField(label = 'Burn-in:', initial = 0.1, max_value = 0.5, min_value = 0.09,
                                help_text = "Always check if more burn-in is needed.")
    seed = forms.IntegerField(label = "Seed:", initial = 123, 
                                help_text = "Change the seed if MCMC chains does not converge.")
    outgroups = forms.CharField(label = "Outgroup taxa names(if any):", required=False, 
                                help_text = "e.g. t1 t2 t3, taxa name separated by a single space, if specified, the tree will be rerooted accordingly." )
    removeog = forms.BooleanField(label = "Remove outgroups(if any):", required=False,
                                help_text = "Remove outgroups that are distant related can improve the delimitation results.")
    sender = forms.EmailField(label='My e-mail address:',
                                help_text = "You can use it to find your results later.")


class jobform(forms.Form):
    job_id = forms.IntegerField(label = "Job id:")
    sender = forms.EmailField(label='E-mail address:')


def index(request):
    #frees, totals = server_stats() 
    #print(frees)
    #print(total)
    #context = {'avaliable':frees, 'total':totals}
    context = {}
    return render(request, 'index.html', context)


def help1(request):
    context = {}
    return render(request, 'ptp/help.html', context)


def thanks(request):
    return HttpResponse("Thanks for using our service!")


def autherror(request):
    return HttpResponse("Job id does not exists or e-mail address does not match!")

def sge_error(request):
    return HttpResponse("There is something wrong with the SGE, please try again later!")

def findjob(request):
    if request.method == 'POST': # If the form has been submitted...
        jform = jobform(request.POST)
        if jform.is_valid():
            email = jform.cleaned_data['sender']
            job_id = jform.cleaned_data['job_id']
            jobs = Jobs.objects.filter(id=job_id)
            if len(jobs) > 0:
                if jobs[0].email != email:
                    return autherror(request)
            else:
                return autherror(request)
            out_path = settings.MEDIA_ROOT + str(job_id) + "/output"
            with open(out_path) as outfile:
                lines = outfile.readlines()
                with open(out_path + ".err") as outfile2:
                    lines2 = outfile2.readlines()
                    if len(lines) > 5:
                        results="<br>".join(lines)
                        context = {'result':results, 'jobid':job_id, 'email':email}
                        return render(request, 'ptp/results.html', context)
                    else:
                        if len(lines2) > 3:
                            return render(request, 'ptp/results.html', {'result':"Something is wrong, please check your input file", 'jobid':job_id, 'email':email})
                        else:
                            return render(request, 'ptp/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email})
    else:
        jform = jobform()
    context = {'jform':jform}
    return render(request, 'ptp/findjob.html', context)


def ptp_index(request):
    frees, totals = server_stats() 
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
            
            nmcmc = ptp_form.cleaned_data['nmcmc']
            imcmc = ptp_form.cleaned_data['imcmc']
            burnin = ptp_form.cleaned_data['burnin']
            seed = ptp_form.cleaned_data['seed']
            outgroups = ptp_form.cleaned_data['outgroups'].strip()
            #print(outgroups)
            removeog = ptp_form.cleaned_data['removeog']
            
            #os.chmod(filepath, 0777)
            if ptp_form.cleaned_data['rooted'] == "rooted":
                jobok = run_ptp(fin = newfilename, fout = filepath + "output", rooted = True, nmcmc = nmcmc, imcmc = imcmc, burnin = burnin, seed = seed, outgroup = outgroups, remove = removeog)
            else:
                jobok = run_ptp(fin = newfilename, fout = filepath + "output", rooted = False, nmcmc = nmcmc, imcmc = imcmc, burnin = burnin, seed = seed, outgroup = outgroups, remove = removeog)
            
            #return HttpResponseRedirect('result/') # Redirect after POST
            #if jobok:
            return show_ptp_result(request, job_id = repr(job.id), email = job.email)
            #else:
            #return sge_error(request)
    else:
        ptp_form = PTPForm() # An unbound form
    context = {'pform':ptp_form, 'avaliable':frees, 'total':totals}
    return render(request, 'ptp/index.html', context)


def show_ptp_result(request, job_id = "", email = ""):
    if job_id == "" or email == "":
        job_id = request.GET.get('job_id', '')
        email = request.GET.get('email', '')
    
    jobs = Jobs.objects.filter(id=job_id)
    if len(jobs) > 0:
        if jobs[0].email != email:
            return autherror(request)
    else:
        return autherror(request)
    
    out_path = settings.MEDIA_ROOT + job_id + "/output"
    outpar = settings.MEDIA_ROOT + job_id +"/output.PTPPartitonSummary.txt"
    outplot = settings.MEDIA_ROOT + job_id + "/output.PTPhSupportPartition.txt.png"
    
    frees, totals = server_stats() 
    
    if os.path.exists(outpar) and os.path.exists(outplot):
        with open(out_path) as outfile:
            lines = outfile.readlines()
            results="<br>".join(lines)
            context = {'result':results, 'jobid':job_id, 'email':email, 'avaliable':frees, 'total':totals}
            return render(request, 'ptp/results.html', context)
    elif os.path.exists(out_path + ".err"):
        with open(out_path + ".err") as outfile2:
            lines2 = outfile2.readlines()
            if len(lines2) > 3:
                return render(request, 'ptp/results.html', {'result':"Something is wrong, please check your input file", 'jobid':job_id, 'email':email, 'avaliable':frees, 'total':totals})
            else:
                return render(request, 'ptp/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email, 'avaliable':frees, 'total':totals})
    else:
        return render(request, 'ptp/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email, 'avaliable':frees, 'total':totals})


def show_phylomap_result(request):
    job_id = request.GET.get('job_id', '')
    out_path_line = settings.MEDIA_ROOT + job_id + "/output.phylomap.line.txt"
    out_path_var = settings.MEDIA_ROOT + job_id + "/output.phylomap.var"
    context = {'jobid':job_id}
    if os.path.exists(out_path_line):
        if os.path.exists(out_path_var):
            with open(out_path_var) as outfile:
                lines = outfile.readlines()
                results="<br>".join(lines)
            context['result'] = results
        return render(request, 'ptp/phylomap.html', context)
    else:
        return HttpResponse("PhyloMap result does not exist, please re-submit your job!")


def handle_uploaded_file(fin, fout):
    with open(fout, 'w+') as destination:
        for chunk in fin.chunks():
            destination.write(chunk)


def run_ptp(fin, fout, nmcmc, imcmc, burnin, seed, outgroup = "" , remove = False,  rooted = False):
    #print(outgroup)
    if rooted:
        if outgroup == "":
            Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
            "-b", str(burnin), "-k", "1"], stdout=open(fout, "w"), stderr=open(fout+".err", "w"))
        else:
            if remove:
                Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-d", "-k", "1"], stdout=open(fout, "w"), stderr=open(fout+".err", "w"))
            else:
                Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-k", "1"], stdout=open(fout, "w"), stderr=open(fout+".err", "w"))
    else:
        if outgroup == "":
            Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
            "-b", str(burnin), "-r", "-k", "1"], stdout=open(fout, "w"), stderr=open(fout+".err", "w"))
        else:
            if remove:
                Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-d", "-k", "1"], stdout=open(fout, "w"), stderr=open(fout+".err", "w"))
            else:
                Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-k", "1"], stdout=open(fout, "w"), stderr=open(fout+".err", "w"))

            
def run_ptp_sge(fin, fout, nmcmc, imcmc, burnin, seed, outgroup = "" , remove = False,  rooted = False):
    command = ""
    if rooted:
        if outgroup == "":
            command = " ".join(["python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), "-b", str(burnin), "-k", "1"])
        else:
            if remove:
                command = " ".join(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-d", "-k", "1"])
            else:
                command = " ".join(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-k", "1"])
    else:
        if outgroup == "":
            command = " ".join(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
            "-b", str(burnin), "-r", "-k", "1"])
        else:
            if remove:
                command = " ".join(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-d", "-k", "1"])
            else:
                command = " ".join(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/bPTP.py", "-t", fin, "-o", fout, "-s", str(seed), "-i", str(nmcmc), "-n", str(imcmc), 
                "-b", str(burnin), "-g", outgroup, "-k", "1"])
    sge_script = generate_sge_script(scommand = command, fout = fout)
    jobok = job_submission(fscript = sge_script)
    return jobok


def server_stats():
    return '0', '0'
    #return avaliable and total slots
    p1 = Popen(['qstat', '-g', 'c'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout = p1.communicate()[0]
    solines = stdout.split("\n")
    sstats = solines[2].split()
    return sstats[4], sstats[5]


def generate_sge_script(scommand, fout):
    with open(fout+".sge.sh", "w") as fsh:
        fsh.write("#!/bin/bash \n")
        fsh.write("#$ -S /bin/bash \n")
        fsh.write("#$ -o "+fout + "\n")
        fsh.write("#$ -e "+fout+".err \n")
        fsh.write("#$ -v DISPLAY \n")
        fsh.write(scommand + "\n")
    return fout+".sge.sh"

    
def job_submission(fscript):
    p1 = Popen(['qsub', fscript], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout = p1.communicate()[0]
    solines = stdout.split("\n")
    if solines[0].endswith("has been submitted"):
        return True
    else:
        return False
        

    

