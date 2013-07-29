from django.db import models

# Create your models here.
class Jobs(models.Model):
    data_type = models.CharField(max_length=20) # ptree, rptree, umtree, alignment, sequences
    method = models.CharField(max_length=10) # GMYC, PTP, CROP, UCLUST
    email = models.EmailField()
    parameter = models.CharField(max_length=100)
    upload_time = models.DateTimeField(auto_now_add = True)
    filepath = models.CharField(max_length=200, default="None")
    