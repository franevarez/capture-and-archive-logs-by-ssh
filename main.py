# -*- coding: utf-8 *-*

# imports
import os
import multiprocessing
import threading
import configparser
import sys
import traceback
import source.process as process

list_logs = []
logs_configs = []
debug_mode = True

def main():
    try:
        # configparser for get configurations
        cur_path = os.path.dirname(os.path.abspath(__file__))

        config = configparser.ConfigParser()
        config.read(cur_path + '/configs/config.ini')
        print(config)

        # diccionary with connections
        logs_configs = config['general']['names'].split(',')

        general_output_rute = config['general']['Output_rute']

        for log_ in logs_configs:
            list_logs.append(process.log_listener(
                log_, config[log_], general_output_rute))

            print(vars(list_logs[0]))

        print(list_logs)
        for run_logs in list_logs:
            process_ = None
            process_ = threading.Thread(target=run_logs.run)
            process_.start()

    except Exception as e:
        if debug_mode:
            print(traceback.format_exc())
        print(
            "\n\nSorry the configuration is bad please read the confiuration in the file README.md or if is a problem "
            "with the code please report franevarez@gmail.com\n")

if __name__ == '__main__':
    main()

