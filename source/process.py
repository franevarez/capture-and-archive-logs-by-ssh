# -*- coding: utf-8 *-*

import os
import sys
import datetime
import traceback
from paramiko import SSHClient, AutoAddPolicy
from shutil import move, rmtree
import threading
import tarfile

os_path = ''

flag_print_logs = True

#principal object per getlogs
class log_listener():
    def __init__(self, name, configuration, generalRute):
        #add all configuration that need
        self.name       = name
        self.ip         = configuration['ip']
        self.port = int(configuration['port'])
        self.user = configuration['user']
        self.password = configuration['password']
        self.rute = configuration['rute_log']
        self.days_to_save = configuration['days_to_save']

        if 'output' in configuration:
            self.output = configuration['output']
        else:
            self.output = generalRute
            
    def run(self):
        date = datetime.datetime.now()
        output_folder = self.check_and_make_dir(date)
        print(output_folder)
        try:
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.user, self.password)

            stdin, stdout, stderr = ssh.exec_command('tail -f '+self.rute)

            # for line in stdout.readlines():
            #     sys.stdout.write(line)
            output_file = open(os.path.join(
                output_folder, "System.log"), "w", encoding="utf-8", errors="ignore")

            process_ = None
            process_ = threading.Thread(target=self.clean_directory())
            process_.start()

            for line in iter(stdout.readline, ""):
                if date.day != datetime.datetime.now().day:
                    date = datetime.datetime.now()#necesary per if
                    output_file.close()
                    output_folder = self.check_and_make_dir(date)
                    output_file = open(os.path.join(
                        output_folder, "System.log"), "w")
                    process_ = None
                    process_ = threading.Thread(target=self.clean_directory())
                    process_.start()
                else:
                    output_file.write(line)
                    
                if flag_print_logs:
                    try:
                        print(line, end="")
                    except:
                        pass
                        
            print('finished.')
            
        except Exception:
            print(traceback.format_exc())
            #self.run()
        #print(self.check_and_make_dir())

    def check_and_make_dir(self, date:str):

        date_name = "\\%s-%s-%s" % (date.year, date.month, date.day)
        try:
            if not os.path.isdir(self.output+'\\'+self.name):
                os.mkdir(self.output+'\\'+self.name)
            self.output_dir = self.output+'\\'+self.name

            if not os.path.isdir(self.output_dir+date_name):
                os.mkdir(self.output_dir+date_name)
                return self.output_dir+date_name
            else:
                c = 1
                while True:
                    if not os.path.isdir(self.output_dir+date_name+"_"+str(c)):
                        os.mkdir(self.output_dir+date_name+"_"+str(c))
                        return self.output_dir+date_name+"_"+str(c)
                    c += 1

        except Exception :
            print(traceback.format_exc())

    def clean_directory(self):
        try:
            list_folders = sorted(os.listdir(self.output_dir),
                                  key=lambda x: os.path.getctime(os.path.join(self.output_dir, x)))

            while len(list_folders) > int(self.days_to_save) :
                rmtree(self.output_dir+'\\'+list_folders[0])
                print(list_folders.pop(0))

            while len(list_folders) > 1:
                target_path = self.output_dir+'\\'+list_folders[0]+'\\'
                if os.path.isfile(target_path+"System.log"):
                    #shutil.make_archive(target_path+"System", 'gztar', target_path, "System.log")
                    tar = tarfile.open(
                        self.output_dir+"\\System.tar.gz", "w:gz")
                    tar.add(target_path+"System.log",
                            arcname=os.path.basename(target_path+"System.log"))
                    tar.close()
                    move(self.output_dir+"\\System.tar.gz",
                                 target_path+"\\System.tar.gz")
                    os.remove(target_path+"System.log")

                print(list_folders.pop(0))

        except Exception:
            print(traceback.format_exc())

