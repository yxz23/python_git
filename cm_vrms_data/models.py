#-*-coding:utf-8-*-
from django.db import models


class Upload_Table(models.Model):
    ShowName = models.CharField(max_length=50, verbose_name=u'显示表名', unique=True)
    UserName = models.CharField(max_length=50, verbose_name =u'上传用户')
    UploadTime = models.DateTimeField(verbose_name=u'上传时间', auto_now=True)

    def delete(self, *args, **kwargs):
        '''删除数据库记录同时要删除对应资源文件'''
        from .data_handler import delete_file
        if delete_file(self.ShowName):
            super(Upload_Table, self).delete(*args, **kwargs)

    def __unicode__(self):
        return "{}_{}".format(self.ShowName, self.UserName)

    class Meta:
        db_table = u"cm_vrms_data_table"
        verbose_name = u"表格文件上传"
        verbose_name_plural = u"表格文件上传"
        permissions = (
                    ('table_upload', u'上传表格文件权限'),
                )
