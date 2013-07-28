# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms

class PTPForm(forms.Form):
    treefile = forms.FileField(label='Phylogenetic tree:')
    rooted = forms.ChoiceField(choices = (("rooted", "Rooted"), ("untrooted", "Unrooted")), widget=forms.RadioSelect)
    sender = forms.EmailField(label='Your e-mail address:')
   

def index(request):
    context = {}
    return render(request, 'index.html', context)


def ptp_index(request):
    if request.method == 'POST': # If the form has been submitted...
        ptp_form = PTPForm(request.POST, request.FILES) # A form bound to the POST data
        if ptp_form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        ptp_form = PTPForm() # An unbound form
    context = {'pform':ptp_form}
    return render(request, 'ptp/index.html', context)
