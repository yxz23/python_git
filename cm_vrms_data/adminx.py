#-*-coding:utf-8-*-
from xadmin.plugins.actions import DeleteSelectedAction
import xadmin

from .data_handler import delete_file
from .models import Upload_Table


class SelectedAppAction(DeleteSelectedAction):
    def delete_models(self, queryset):
        '''删除目录中对应资源文件'''
        for data in queryset:
            print data.ShowName
            if not delete_file(data.ShowName):
                return
        super(SelectedAppAction, self).delete_models(queryset)


class Upload_Table_Admin(object):
    actions = [SelectedAppAction, ]
    list_display = ('ShowName', 'UserName', 'UploadTime')
    list_filter = ('ShowName', 'UserName', 'UploadTime')
    ordering = ('-UploadTime', 'ShowName', 'UserName')
    reversion_enable = True

#注册到后台管理
xadmin.site.register(Upload_Table, Upload_Table_Admin)