#!/usr/bin/env python
import os
import sys

'''updated at 0614'''
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cm_vrms_upload.settings")

    from django.core.management import execute_from_command_line
    #order_list = ["runserver","shell","syncdb",'inspectdb']
    #sys.argv = ['C:\\DEV\\PythonWork\\cm_vrms\\manage.py', 'runserver','0.0.0.0:8000']
    
    execute_from_command_line(sys.argv)
