#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# Copyright 2013 Paridin Company (restrada@paridin.com), BSD-style copyright and disclaimer apply
# Last update 08/15/2013
# Purpose daemon for starting, stopping, restarting Nginx and uWsgi services
# Version 1.0
import os
import sys
import subprocess
import psutil

class StartServer:
    """
    Change the paths for your system
    This script run when you have installed uWSGI and nGinx for develop your Django Projects
    """
    nGinxPathPid = '/usr/local/logs'
    uWSGIPathPid = '/tmp'
    nGinxPathBin = '/usr/local/sbin'
    virtualPath = '/Users/paridin/djProjects/bin'
    nginxPid = 9999999  # Initialization of PID out of range
    uWSGIPid = 9999999  # Initialization of PID out of range

    def __init__(self, status):
        """
        Initialization of server nginx and uWSGI
        """
        if self.getNginxPid() != "" and self.getuWSGIPid() != "":
            self.nginxPid = int(self.getNginxPid())
            self.uWSGIPid = int(self.getuWSGIPid())

        if status == 'start':
            if psutil.pid_exists(self.nginxPid) and psutil.pid_exists(self.uWSGIPid):
                return self.statusServer(True)
            else:
                if self.run():
                    return self.statusServer(True)
        elif status == 'stop':
            if psutil.pid_exists(self.nginxPid) or psutil.pid_exists(self.uWSGIPid):
                if self.stop():
                    return self.statusServer(False)
        elif status == 'restart':
            if psutil.pid_exists(self.nginxPid) or psutil.pid_exists(self.uWSGIPid) or not \
                    psutil.pid_exists(self.nginxPid) or not psutil.pid_exists(self.uWSGIPid):
                if self.restart():
                    self.statusServer(None)
        else:
            self.help()
            sys.exit(-1)
        sys.exit(1)

    def statusServer(self, status):
        if status is True:
            print "The Server is Up"
        elif status is False:
            print "The Server is Down"
        else:
            print "The Server was Restarting"

    def getProjectName(self):
        return os.path.dirname(os.path.realpath(__file__))

    def getNginxPid(self):
        if os.path.isfile("%s/nginx.pid" % self.nGinxPathPid):
            pid = subprocess.Popen("cat %s/nginx.pid" % self.nGinxPathPid,
                                   shell=True, stdout=subprocess.PIPE).stdout.read().split('\n')[0]
        else:
            pid = self.nginxPid
        return pid

    def getuWSGIPid(self):
        fileName = self.getProjectName().split('/')[-1]
        if os.path.isfile("%s/%s.pid" % (self.uWSGIPathPid, fileName)):
            pid = subprocess.Popen("cat %s/%s.pid" % (self.uWSGIPathPid, fileName),
                                   shell=True, stdout=subprocess.PIPE).stdout.read().split('\n')[0]
        else:
            pid = self.uWSGIPid
        return pid

    def run(self):
        """
            Starting Nginx and uWSGI services
        """
        nameProject = self.getProjectName()
        fileName = nameProject.split('/')[-1]
        # Start Nginx
        subprocess.Popen("sudo %s/nginx" % self.nGinxPathBin,
                                  shell=True, stdout=subprocess.PIPE)
        # Start uWSGI
        subprocess.Popen("sudo %s/uwsgi --ini %s/conf/%s_uwsgi.ini" % (self.virtualPath, nameProject, fileName),
                         shell=True, stdout=subprocess.PIPE)
        # Getting PIDs services of Nginx and uWSGI
        self.nginxPid = self.getNginxPid()
        self.uWSGIPid = self.getuWSGIPid()

        if self.nginxPid and self.uWSGIPid:
            return True
        else:
            return False

    def stop(self):
        """
            Stopping Nginx and uWSGI services
        """
        try:
            #Down Nginx
            nginxChild = psutil.Process(self.nginxPid)
            nginxChild.terminate()
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            print "couldn't kill child process with pid %s" % self.nginxPid
        else:
            nginxChild.wait(timeout=3)
        try:
            #Down uWSGI
            uWSGIChild = psutil.Process(self.uWSGIPid)
            uWSGIChild.kill()
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            print "couldn't kill child process with pid %s" % self.uWSGIPid
        else:
            uWSGIChild.wait(timeout=3)

        # Check if nginx pid is off and uWSGI pid is off
        if not psutil.pid_exists(self.nginxPid) and not psutil.pid_exists(self.uWSGIPid):
            # Nginx and uWSGI services is down
            return True
        else:
            # Nginx and uWSGI services are alive
            return False

    def restart(self):
        """
            Restarting Nginx and uWSGI services
        """
        nameProject = self.getProjectName()
        fileName = nameProject.split('/')[-1]
        try:
            #Down Nginx
            nginxChild = psutil.Process(self.nginxPid)
            nginxChild.terminate()
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            print "couldn't kill child process with pid %s" % self.nginxPid
        else:
            nginxChild.wait(timeout=3)
        try:
            #Down uWSGI
            uWSGIChild = psutil.Process(self.uWSGIPid)
            uWSGIChild.kill()
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            print "couldn't kill child process with pid %s" % self.uWSGIPid
        else:
            uWSGIChild.wait(timeout=3)
        print "Down the services Nginx, uWSGI"
        # Start Nginx services
        subprocess.Popen("sudo %s/nginx" % self.nGinxPathBin,
                                  shell=True, stdout=subprocess.PIPE)
        # Start uWSGI service
        subprocess.Popen("sudo %s/uwsgi --ini %s/conf/%s_uwsgi.ini" % (self.virtualPath, nameProject, fileName),
                   shell=True, stdout=subprocess.PIPE)
        print "Up the services Nginx, uWSGI"
        # Rewrite PID Variables
        self.nginxPid = int(self.getNginxPid())
        self.uWSGIPid = int(self.getuWSGIPid())
        # Validate if nginx is run use a stdout of process and pid's of nginx and uWSGI
        if psutil.pid_exists(self.uWSGIPid) and psutil.pid_exists(self.nginxPid):
            return True
        else:
            return False

    def help(self):
        # Help can be use to know how execute the source
        print "for run this script you need use \n sudo python start_server.py [stop|start|restart]"


if __name__ == '__main__':
        if os.geteuid() == 0:
            if len(sys.argv) == 2:
                StartServer(sys.argv[1])
            else:
                StartServer(sys.argv[0]).help()
        else:
                sys.exit('You need be superuser [root] to run this script. \nTry again like root user.')