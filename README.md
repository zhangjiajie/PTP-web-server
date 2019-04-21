sd_web
======
Species delimitation web server

Provide web interface for PTP and GMYC

Requires Django 1.11 and python 3.6 

Deploy:
- Download and Install PTP
- Install X server if needed
- Clone web server into /webdata/sd_web/ 
- Change settings.py to the deployment enviroment:
    in settings.py set MEDIA_ROOT = /webdata/sd_web/sd_server/upload/
    change permissions, particular for the R script
    copy executable (bPTP.py, summary.py and gmyc.script.R) to MEDIA_ROOT/bin
- Install R depency
- Setup Torque PBS
- python3 manage.py runserver


X-Server
========
See this page how to install and configure X server:
http://pythonhosted.org/ete2/tutorial/tutorial_webplugin.html#servers
https://groups.google.com/forum/#!searchin/etetoolkit/x$20server$20/etetoolkit/XSIeQyX9W64/0mPc4n1SrDMJ


Apache
======
Add this to /etc/apache2/httpd.conf:
FastCGIExternalServer /webdata/sd_web/sd_server/sd_server.fcgi -host 193.197.73.70:2222

Add this to /etc/apache2/sites-enabled/000-default:
<VirtualHost *:80>
  ServerName species.h-its.org
  DocumentRoot /webdata/sd_web/sd_server
  #alias /static /webdata/sd_web/sd_server/static
  #alias /download /webdata/sd_web/sd_server/download
  RewriteEngine On
  RewriteRule ^/(static.*)$ /$1 [QSA,L,PT]
  #RewriteRule ^/(download.*)$ /$1 [QSA,L,PT]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteRule ^/(.*)$ /sd_server.fcgi/$1 [QSA,L]
</VirtualHost>
 
export DISPLAY=localhost:0.0
python manage.py runfcgi method=threaded host=193.197.73.70 port=2222

sudo service apache2 restart

GMYC
====
sudo apt-get install liblapack-dev liblapack3 libopenblas-base libopenblas-dev r-base-dev r-base

INSTALL R GMYC:
install.packages("ape",repos="http://cran.r-project.org/")
install.packages("paran",repos="http://cran.r-project.org/")
install.packages("splits",repos="http://R-Forge.R-project.org")

$Rscript gmyc.script.R tree method

input: an input tree in newick or nexus format (its name should end with ".tre" or ".nex".
method: type of method, s for single and m for multiple threshold.

(you can make it executable if Rscript is installed as /usr/bin/Rscript, like other linux scripts)

It outputs following files.

xxxx_list: a tab-delimited text file of delimitation. it is an output of the spec.list function.
xxxx_summary: a text file of summary of analysis from summary.gmyc.
xxxx_plot.pdf: plots in pdf format.
xxxx_plot.png: plots in png format.


Torque
======
sudo apt-get install torque-server torque-client torque-mom torque-pam torque-scheduler

/etc/init.d/torque-mom stop
/etc/init.d/torque-scheduler stop
/etc/init.d/torque-server stop

sudo pbs_server -t create
sudo killall pbs_server

sudo echo torque.localhost > /etc/torque/server_name
sudo echo torque.localhost > /var/spool/torque/server_priv/acl_svr/acl_hosts
sudo echo root@torque.localhost > /var/spool/torque/server_priv/acl_svr/operators
sudo echo root@torque.localhost > /var/spool/torque/server_priv/acl_svr/managers

echo "torque.localhost np=2" > /var/spool/torque/server_priv/nodes

echo torque.localhost > /var/spool/torque/mom_priv/config


sudo /etc/init.d/torque-server start
sudo /etc/init.d/torque-scheduler start
sudo /etc/init.d/torque-mom start


# set scheduling properties, looks like this takes some time
sudo qmgr -c 'set server scheduling = true'
sudo qmgr -c 'set server keep_completed = 300'
sudo qmgr -c 'set server mom_job_sync = true'


# create default queue
qmgr -c 'create queue batch'
qmgr -c 'set queue batch queue_type = execution'
qmgr -c 'set queue batch started = true'
qmgr -c 'set queue batch enabled = true'
qmgr -c 'set queue batch resources_default.walltime = 1:00:00'
qmgr -c 'set queue batch resources_default.nodes = 1'
qmgr -c 'set server default_queue = batch'


# configure submission pool
qmgr -c 'set server submit_hosts = torque'
qmgr -c 'set server allow_node_submit = true'

sudo echo localhost > /etc/hosts.equiv


https://jabriffa.wordpress.com/2015/02/11/installing-torquepbs-job-scheduler-on-ubuntu-14-04-lts/
http://linuxtoolkit.blogspot.com/2014/06/bad-uid-for-job-execution-msgruserok.html
http://docs.adaptivecomputing.com/torque/4-2-7/Content/topics/12-appendices/commandsOverview.htm
