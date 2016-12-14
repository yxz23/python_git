# encoding: utf-8#
from cm_vrms_wiki.models import *
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from django.utils.translation import ugettext as _, ugettext_lazy

from xadmin import views
from xadmin.plugins.actions import DeleteSelectedAction
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction
from xadmin.views.base import ModelAdminView, filter_hook, csrf_protect_m
import xadmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from reversion.models import Revision, Version
from .wikiManager import WikiManager


class MainDashboard(object):
    '''widgets 小插件'''
    widgets = [
        [
            {
                "type": "html",
                "title": "后台首页",
                "content": "<h3>License过期列表</h3><iframe frameborder='0' width='800px' height = '800px' src='/alert_info/'></iframe>"

            },
        ]
    ]


xadmin.site.register(views.website.IndexView, MainDashboard)


class SelectedAction(DeleteSelectedAction):
    def delete_models(self, queryset):
        super(SelectedAction, self).delete_models(queryset)
        WikiManager().set_changed(True)


class CM_ApplicationAdmin(object):
    # 列表页，列表顶部显示的字段名称
    # show_detail_fields = ['AppID', 'Category','ChineseName']
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('AppID',
                    'Category', 'ChineseName', 'EnglishName',
                    'UATVersion', 'ServiceType',
                    'Status', 'LaunchDate', 'UatRelease',
                    'ProdRelease',)
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('AppID',
                   'Category', 'ChineseName', 'EnglishName',
                   'UATVersion', 'ServiceType',
                   'Status', 'LaunchDate', 'UatRelease',
                   'ProdRelease',)
    fields = ('AppID', 'Category', 'ChineseName',
              'EnglishName',
              'UATVersion', 'ServiceType',
              'Status', 'LaunchDate',
              'OffDate', 'ServiceStart', 'ServiceEnd',
              'OperationStart', 'AvailableDate',
              'UatRelease', 'ProdRelease', 'Description', 'UpdateDate', 'Remark')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('AppID',)
    # 表格列表可编辑

    list_editable = ['AppID',
                     'Category', 'ChineseName', 'EnglishName',
                     'UATVersion', 'ServiceType',
                     'Status', 'LaunchDate', 'UatRelease',
                     'ProdRelease', ]
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(CM_Application, CM_ApplicationAdmin)


class CM_Application_MaintainerAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ID', 'AppID',
                    'DeptName', 'CMA', 'CMB',
                    'DeilverA', 'DeilverB', 'DevPM',
                    'DevCompany', 'DevCompanyPM', 'TestPM',
                    'TestLD',)
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ID', 'AppID',
                   'DeptName',
                   'DevCompany', 'DevCompanyPM', 'TestPM',
                   'TestLD',)
    fields = ('ID', 'AppID',
              'DeptName', 'CMA', 'CMB',
              'DeilverA', 'DeilverB', 'DevPM',
              'DevCompany', 'DevCompanyPM', 'TestPM',
              'TestLD',)
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ID',)
    # 表格列表可编辑

    list_editable = ['ID', 'AppID',
                     'DeptName', 'CMA', 'CMB',
                     'DeilverA', 'DeilverB', 'DevPM',
                     'DevCompany', 'DevCompanyPM', 'TestPM',
                     'TestLD', ]
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(CM_Application_Maintainer, CM_Application_MaintainerAdmin)


class SelectedAppAction(DeleteSelectedAction):
    def delete_models(self, queryset):
        '''添加到历史表'''
        for data in queryset:
            his = AppserverHistory(
                Device=data.DeviceID,
                Application=unicode(data.AppID).split('\t')[1],
                HostName=data.HostName,
                OSVersion=data.OSVersion,
                ServiceIP=data.ServiceIP
            )
            his.save()

        super(SelectedAppAction, self).delete_models(queryset)
        WikiManager().set_changed(True)


class AppserverAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAppAction, ]
    save_as = True
    list_display = ('AppServerID', 'DeviceID', 'CluserID',
                    'AppID', 'HostName', 'LogicHostname', 'OsName',
                    'OSVersion', 'CpuSpeed', 'CpuNum',
                    'MemorySize', 'DiskSize',
                    'ServerIP', 'ServiceIP',
                    'LBIP', 'Usage', 'Remark', 'Remark1', 'UpdateTime')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('AppServerID', 'DeviceID', 'CluserID',
                   'AppID', 'HostName', 'LogicHostname', 'OsName',
                   'OSVersion', 'CpuSpeed', 'CpuNum',
                   'MemorySize', 'DiskSize',
                   'ServerIP', 'ServiceIP',
                   'LBIP', 'Usage', 'Remark', 'UpdateTime')
    fields = ('AppServerID', 'DeviceID', 'CluserID',
              'AppID', 'HostName', 'LogicHostname', 'OsName',
              'OSVersion', 'CpuSpeed', 'CpuNum',
              'MemorySize', 'DiskSize',
              'ServerIP', 'ServiceIP',
              'LBIP', 'Usage', 'Remark', 'Remark1', 'UpdateTime')
    # 自然是排序所用了，减号代表降序排列

    # filter_horizontal = ('StorageDeviceId',)
    # raw_id_fields = ('StorageDeviceId',)
    # style_fields = {'StorageDeviceId': 'm2m_transfer'}
    ordering = ('-UpdateTime', 'AppServerID', 'AppID',)
    # 表格列表可编辑

    # list_editable = ['AppServerID', 'DeviceID','CluserID',
    # 'AppID', 'HostName', 'OsName',
    # 'OSVersion','CpuSpeed','CpuNum',
    # 'MemorySize','DiskSize',
    # 'ServerIP','ServiceIP',
    # 'LBIP']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Appserver, AppserverAdmin)


class AppserverHisAdmin(object):
    # 列表页，列表顶部显示的字段名称
    list_display = ('Device', 'Application', 'HostName', 'OSVersion', 'ServiceIP', 'DeleteTime')

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('Device', 'Application', 'HostName', 'OSVersion', 'ServiceIP', 'DeleteTime')

    ordering = ('-DeleteTime',)

    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(AppserverHistory, AppserverHisAdmin)


class ImageStoreAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('AppID', 'name',
                    'img')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('AppID', 'name',
                   'img')
    fields = ('AppID', 'name',
              'img')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('AppID', 'name',)
    # 表格列表可编辑

    list_editable = ['AppID', 'name',
                     'img']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(ImageStore, ImageStoreAdmin)


class MountAdmin(object):
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('MountID', 'StorageDeviceId',
                    'AppServerID', 'MountPath')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('MountID', 'StorageDeviceId',
                   'AppServerID', 'MountPath')
    fields = ('MountID',
              'AppServerID', 'MountPath')
    # 自然是排序所用了，减号代表降序排列

    ordering = ('MountID', 'StorageDeviceId',
                'AppServerID',)
    # 表格列表可编辑

    list_editable = ['MountID', 'StorageDeviceId',
                     'AppServerID', 'MountPath']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Mount, MountAdmin)


class LBAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('LBID', 'AppID',
                    'LBName', 'LBIP')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('LBID', 'AppID',
                   'LBName', 'LBIP')
    fields = ('LBID', 'AppID',
              'LBName', 'LBIP')
    # 自然是排序所用了，减号代表降序排列

    ordering = ('LBID', 'AppID',)
    # 表格列表可编辑

    list_editable = ['LBID', 'AppID',
                     'LBName', 'LBIP']
    reversion_enable = True


xadmin.site.register(LB, LBAdmin)


class LB_MemberAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('LBID', 'AppID',
                    'AppServerID', 'AppServerIP')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('LBID', 'AppID',
                   'AppServerID', 'AppServerIP')
    fields = ('LBID', 'AppID',
              'AppServerID', 'AppServerIP')
    # 自然是排序所用了，减号代表降序排列

    ordering = ('LBID', 'AppID',
                'AppServerID', 'AppServerIP')
    # 表格列表可编辑

    list_editable = ['LBID', 'AppID',
                     'AppServerID', 'AppServerIP']
    reversion_enable = True


xadmin.site.register(LB_Member, LB_MemberAdmin)


class CM_UsersAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('UserID', 'AppServerID',
                    'UserName', 'UserType', 'ExpirationDate', 'PGroupName',
                    'SGroupName')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('UserID', 'AppServerID',
                   'UserName', 'UserType', 'ExpirationDate', 'PGroupName',
                   'SGroupName')
    fields = ('UserID', 'AppServerID',
              'UserName', 'UserType', 'ExpirationDate', 'PGroupName',
              'SGroupName')
    # 自然是排序所用了，减号代表降序排列

    ordering = ('UserID', 'AppServerID',)
    # 表格列表可编辑

    list_editable = ['UserID', 'AppServerID',
                     'UserName', 'UserType', 'ExpirationDate', 'PGroupName',
                     'SGroupName']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(CM_Users, CM_UsersAdmin)


class Config_FileAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ConfigId', 'AppServerID',
                    'ConfigName', 'UserID',
                    'ConfigDescription')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ConfigId', 'AppServerID',
                   'ConfigName', 'UserID')
    fields = ('ConfigId', 'AppServerID',
              'ConfigName', 'UserID',
              'ConfigDescription')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ConfigId', 'AppServerID',)
    # 表格列表可编辑

    list_editable = ['ConfigId', 'AppServerID',
                     'ConfigName', 'UserID',
                     'ConfigDescription']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Config_File, Config_FileAdmin)


class Config_ItemAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ConfigItemId', 'ConfigName',
                    'Parameter', 'value',
                    'bl1', 'bl2', 'ConfigDescription')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ConfigItemId', 'ConfigName',
                   'Parameter', 'value',
                   'bl1', 'bl2')
    fields = ('ConfigItemId', 'ConfigName',
              'Parameter', 'value',
              'bl1', 'bl2', 'ConfigDescription')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ConfigItemId', 'ConfigName',
                'Parameter',)
    # 表格列表可编辑

    list_editable = ['ConfigItemId', 'ConfigName',
                     'Parameter', 'value',
                     'bl1', 'bl2', 'ConfigDescription']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Config_Item, Config_ItemAdmin)


class Log_FileAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('LogId', 'AppServerID',
                    'UserID', 'LogPath', 'LogDescription',
                    'LifeCycle')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('LogId', 'AppServerID',
                   'UserID')
    fields = ('LogId', 'AppServerID',
              'UserID', 'LogPath', 'LogDescription',
              'LifeCycle')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('LogId', 'AppServerID', 'UserID',)
    # 表格列表可编辑

    list_editable = ['LogId', 'AppServerID',
                     'UserID', 'LogPath', 'LogDescription',
                     'LifeCycle']
    reversion_enable = True


xadmin.site.register(Log_File, Log_FileAdmin)


class Server_Process_PoolAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ProcessId', 'AppServerID',
                    'UserID', 'ProcessName', 'Port',
                    'Function')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ProcessId', 'AppServerID',
                   'UserID', 'ProcessName')
    fields = ('ProcessId', 'AppServerID',
              'UserID', 'ProcessName', 'Port',
              'Function')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ProcessId', 'AppServerID', 'UserID',)
    # 表格列表可编辑

    list_editable = ['ProcessId', 'AppServerID',
                     'UserID', 'ProcessName', 'Port',
                     'Function']
    reversion_enable = True


xadmin.site.register(Server_Process_Pool, Server_Process_PoolAdmin)


class SoftwareAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('SoftwareID', 'AppServerID',
                    'SoftwareType', 'SoftwareName', 'InstallPath',
                    'Version')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('SoftwareID', 'AppServerID',
                   'SoftwareType', 'SoftwareName')
    fields = ('SoftwareID', 'AppServerID',
              'SoftwareType', 'SoftwareName', 'InstallPath',
              'Version')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('SoftwareID', 'AppServerID',)
    # 表格列表可编辑

    list_editable = ['SoftwareID', 'AppServerID',
                     'SoftwareType', 'SoftwareName', 'InstallPath',
                     'Version']
    reversion_enable = True


xadmin.site.register(Software, SoftwareAdmin)


class WeblogicAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('WeblogicID', 'SoftwareID',
                    'ConsoleContexPath', 'ConsoleUserName', 'DomianName',
                    'DomainPath', 'WeblogicServerName', 'Listener',
                    'SSLListener', 'JDBCType', 'JNDIName', 'JDBCUrl',
                    'Driver')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('WeblogicID', 'SoftwareID',
                   'ConsoleUserName', 'DomianName')
    fields = ('WeblogicID', 'SoftwareID',
              'ConsoleContexPath', 'ConsoleUserName', 'DomianName',
              'DomainPath', 'WeblogicServerName', 'Listener',
              'SSLListener', 'JDBCType', 'JNDIName', 'JDBCUrl',
              'Driver')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('WeblogicID', 'SoftwareID',)
    # 表格列表可编辑

    list_editable = ['WeblogicID', 'SoftwareID',
                     'ConsoleContexPath', 'ConsoleUserName', 'DomianName',
                     'DomainPath', 'WeblogicServerName', 'Listener',
                     'SSLListener', 'JDBCType', 'JNDIName', 'JDBCUrl',
                     'Driver']
    reversion_enable = True


xadmin.site.register(Weblogic, WeblogicAdmin)


class Weblogic_JdbcAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('JdbcID', 'WeblogicID',
                    'JDBCType', 'JNDIName', 'JDBCUrl',
                    'Driver')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('JdbcID', 'WeblogicID',
                   'JDBCType', 'JNDIName', 'JDBCUrl',
                   'Driver')
    fields = ('JdbcID', 'WeblogicID',
              'JDBCType', 'JNDIName', 'JDBCUrl',
              'Driver')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('JdbcID', 'WeblogicID',)
    # 表格列表可编辑

    list_editable = ['JdbcID', 'WeblogicID',
                     'JDBCType', 'JNDIName', 'JDBCUrl',
                     'Driver']
    reversion_enable = True


xadmin.site.register(Weblogic_Jdbc, Weblogic_JdbcAdmin)


class Weblogic_ServerAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ServerID', 'WeblogicID',
                    'WeblogicServerName', 'Listener',
                    'SSLListener')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ServerID', 'WeblogicID',
                   'WeblogicServerName', 'Listener',
                   'SSLListener')
    fields = ('ServerID', 'WeblogicID',
              'WeblogicServerName', 'Listener',
              'SSLListener')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ServerID', 'WeblogicID',)
    # 表格列表可编辑

    list_editable = ['ServerID', 'WeblogicID',
                     'WeblogicServerName', 'Listener',
                     'SSLListener']
    reversion_enable = True


xadmin.site.register(Weblogic_Server, Weblogic_ServerAdmin)


class Weblogic_Jdbc_MapAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ServerID', 'JdbcID')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ServerID', 'JdbcID')
    fields = ('ServerID', 'JdbcID')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ServerID', 'JdbcID',)
    # 表格列表可编辑

    list_editable = ['ServerID', 'JdbcID']
    reversion_enable = True


xadmin.site.register(Weblogic_Jdbc_Map, Weblogic_Jdbc_MapAdmin)


class Weblogic_AppAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('AppID', 'ServerID',
                    'AppName', 'DeployPath', 'DeployType',
                    'Description')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('AppID', 'ServerID',
                   'AppName')
    fields = ('AppID', 'ServerID',
              'AppName', 'DeployPath', 'DeployType',
              'Description')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('AppID', 'ServerID',)
    # 表格列表可编辑

    list_editable = ['AppID', 'ServerID',
                     'AppName', 'DeployPath', 'DeployType',
                     'Description']
    reversion_enable = True


xadmin.site.register(Weblogic_App, Weblogic_AppAdmin)


class LicenseAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('LicenseID', 'AppID',
                    'AppServerID', 'Software', 'Version',
                    'DueDate', 'Company',
                    'Remark')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('LicenseID', 'AppID',
                   'AppServerID', 'Software', 'Version',
                   'DueDate', 'Company')
    fields = ('LicenseID', 'AppID',
              'AppServerID', 'Software', 'Version',
              'DueDate', 'Company',
              'Remark')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('LicenseID', 'AppID',
                'AppServerID',)
    # 表格列表可编辑

    list_editable = ['LicenseID', 'AppID',
                     'AppServerID', 'Software', 'Version',
                     'DueDate', 'Company',
                     'Remark']
    reversion_enable = True


xadmin.site.register(License, LicenseAdmin)


class DBAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('DBID', 'SoftwareID',
                    'INSTANCE_NAME', 'DBName', 'DataFile',
                    'LogFile', 'Port',
                    'DbUser', 'HA', 'MEMBER')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('DBID', 'SoftwareID',
                   'INSTANCE_NAME', 'DBName', 'DataFile',
                   'LogFile', 'Port',
                   'DbUser', 'HA', 'MEMBER')
    fields = ('DBID', 'SoftwareID',
              'INSTANCE_NAME', 'DBName', 'DataFile',
              'LogFile', 'Port',
              'DbUser', 'HA', 'MEMBER')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('DBID', 'SoftwareID',)
    # 表格列表可编辑

    list_editable = ['DBID', 'SoftwareID',
                     'INSTANCE_NAME', 'DBName', 'DataFile',
                     'LogFile', 'Port',
                     'DbUser', 'HA', 'MEMBER']
    reversion_enable = True


xadmin.site.register(DB, DBAdmin)


class MQAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('MQID', 'SoftwareID',
                    'QueueManager', 'QLocal', 'QRemote',
                    'Chanel', 'Port')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('MQID', 'SoftwareID',
                   'QueueManager', 'QLocal', 'QRemote',
                   'Chanel', 'Port')
    fields = ('MQID', 'SoftwareID',
              'QueueManager', 'QLocal', 'QRemote',
              'Chanel', 'Port')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('MQID', 'SoftwareID',)
    # 表格列表可编辑

    list_editable = ['MQID', 'SoftwareID',
                     'QueueManager', 'QLocal', 'QRemote',
                     'Chanel', 'Port']
    reversion_enable = True


xadmin.site.register(MQ, MQAdmin)


class TomcatAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('TomcatID', 'SoftwareID',
                    'Port', 'SSLPort', 'DocmentRoot')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('TomcatID', 'SoftwareID',
                   'Port', 'SSLPort', 'DocmentRoot')
    fields = ('TomcatID', 'SoftwareID',
              'Port', 'SSLPort', 'DocmentRoot')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('TomcatID', 'SoftwareID',)
    # 表格列表可编辑

    list_editable = ['TomcatID', 'SoftwareID',
                     'Port', 'SSLPort', 'DocmentRoot']
    reversion_enable = True


xadmin.site.register(Tomcat, TomcatAdmin)


class ApacheAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ApacheID', 'SoftwareID',
                    'Port', 'SSLPort', 'DocmentRoot')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ApacheID', 'SoftwareID',
                   'Port', 'SSLPort', 'DocmentRoot')
    fields = ('ApacheID', 'SoftwareID',
              'Port', 'SSLPort', 'DocmentRoot')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ApacheID', 'SoftwareID',)
    # 表格列表可编辑

    list_editable = ['ApacheID', 'SoftwareID',
                     'Port', 'SSLPort', 'DocmentRoot']
    reversion_enable = True


xadmin.site.register(Apache, ApacheAdmin)


class OtherAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('OtherID', 'SoftwareID',
                    'Description')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('OtherID', 'SoftwareID')
    fields = ('OtherID', 'SoftwareID', 'Description')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('OtherID', 'SoftwareID',)
    # 表格列表可编辑

    list_editable = ['OtherID', 'SoftwareID',
                     'Description']
    reversion_enable = True


xadmin.site.register(Other, OtherAdmin)


class CluserAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('CluserID', 'VCenter', 'CluserName')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('CluserID', 'VCenter', 'CluserName')
    fields = ('CluserID', 'VCenter', 'CluserName')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('CluserID',)
    # 表格列表可编辑

    list_editable = ['CluserID', 'VCenter', 'CluserName']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Cluser, CluserAdmin)


class DeviceAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('DeviceID', 'DeviceSN', 'MANUFACTURER',
                    'CATEGORY', 'PURCHASE_DATE', 'maintainerA', 'maintainerB',
                    'DISTRICT', 'ROOM', 'CABINET',
                    'COUNT_U')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('DeviceID', 'DeviceSN', 'MANUFACTURER',
                   'CATEGORY', 'PURCHASE_DATE', 'maintainerA', 'maintainerB',
                   'DISTRICT', 'ROOM', 'CABINET',
                   'COUNT_U')
    fields = ('DeviceID', 'DeviceSN', 'MANUFACTURER',
              'CATEGORY', 'PURCHASE_DATE', 'maintainerA', 'maintainerB',
              'DISTRICT', 'ROOM', 'CABINET',
              'COUNT_U', 'REMARK', 'UpdateTime')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('DeviceID',)
    # 表格列表可编辑

    list_editable = ['DeviceID', 'DeviceSN', 'MANUFACTURER',
                     'CATEGORY', 'PURCHASE_DATE', 'maintainerA', 'maintainerB',
                     'DISTRICT', 'ROOM', 'CABINET',
                     'COUNT_U']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Device, DeviceAdmin)


class server_detailAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('ServerId', 'DeviceID',
                    'ServerName', 'DeviceSN', 'Server_type',
                    'CPU_TYPE', 'CPU_FREQUENCY', 'CPU_NUM',
                    'CPU_CORE_NUM', 'MEM_TYPE', 'MEM_CONF',
                    'MEM_SIZE', 'HARDDISK_CAPACITY', 'DISK_SIZE',
                    'NETWORK_CARD', 'HBACARD')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('ServerId', 'DeviceID',
                   'ServerName', 'DeviceSN', 'Server_type')
    fields = ('ServerId', 'DeviceID',
              'ServerName', 'DeviceSN', 'Server_type',
              'CPU_TYPE', 'CPU_FREQUENCY', 'CPU_NUM',
              'CPU_CORE_NUM', 'MEM_TYPE', 'MEM_CONF',
              'MEM_SIZE', 'HARDDISK_CAPACITY', 'DISK_SIZE',
              'NETWORK_CARD', 'HBACARD')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('ServerId', 'DeviceID',)
    # 表格列表可编辑

    list_editable = ['ServerId', 'DeviceID',
                     'ServerName', 'DeviceSN', 'Server_type',
                     'CPU_TYPE', 'CPU_FREQUENCY', 'CPU_NUM',
                     'CPU_CORE_NUM', 'MEM_TYPE', 'MEM_CONF',
                     'MEM_SIZE', 'HARDDISK_CAPACITY', 'DISK_SIZE',
                     'NETWORK_CARD', 'HBACARD']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(server_detail, server_detailAdmin)


class storage_detailAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('StorageId', 'DeviceID',
                    'STORAGE_NAME', 'DeviceSN', 'Firmware',
                    'Ctlr_NUM', 'DISK_TYPE', 'DISK_Capacity',
                    'DISK_NUM', 'IP', 'EXPANSIBILITY')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('StorageId', 'DeviceID',
                   'STORAGE_NAME', 'DeviceSN', 'Firmware',
                   'Ctlr_NUM', 'DISK_TYPE', 'DISK_Capacity',
                   'DISK_NUM', 'IP', 'EXPANSIBILITY')
    fields = ('StorageId', 'DeviceID',
              'STORAGE_NAME', 'DeviceSN', 'Firmware',
              'Ctlr_NUM', 'DISK_TYPE', 'DISK_Capacity',
              'DISK_NUM', 'IP', 'EXPANSIBILITY')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('StorageId', 'DeviceID',)
    # 表格列表可编辑

    list_editable = ['StorageId', 'DeviceID',
                     'STORAGE_NAME', 'DeviceSN', 'Firmware',
                     'Ctlr_NUM', 'DISK_TYPE', 'DISK_Capacity',
                     'DISK_NUM', 'IP', 'EXPANSIBILITY']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(storage_detail, storage_detailAdmin)


class NetDevice_detailAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('NetDeviceId', 'DeviceID',
                    'DeviceSN', 'NetDeviceType', 'MANAGE_IP',
                    'IOS_VERSION')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('NetDeviceId', 'DeviceID',
                   'DeviceSN', 'NetDeviceType', 'MANAGE_IP',
                   'IOS_VERSION')
    fields = ('NetDeviceId', 'DeviceID',
              'DeviceSN', 'NetDeviceType', 'MANAGE_IP',
              'IOS_VERSION')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('NetDeviceId', 'DeviceID',)
    # 表格列表可编辑

    list_editable = ['NetDeviceId', 'DeviceID',
                     'DeviceSN', 'NetDeviceType', 'MANAGE_IP',
                     'IOS_VERSION']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(NetDevice_detail, NetDevice_detailAdmin)


class Equipment_detailAdmin(object):
    # 列表页，列表顶部显示的字段名称
    actions = [SelectedAction, ]
    save_as = True
    list_display = ('EquipmentId', 'DeviceID',
                    'DeviceSN', 'Description')
    # 列表页出现搜索框，参数是搜索的域

    # 右侧会出现过滤器，根据字段类型，过滤器显示过滤选项
    list_filter = ('EquipmentId', 'DeviceID',
                   'DeviceSN', 'Description')
    fields = ('EquipmentId', 'DeviceID',
              'DeviceSN', 'Description')
    # 自然是排序所用了，减号代表降序排列
    ordering = ('EquipmentId', 'DeviceID',)
    # 表格列表可编辑

    list_editable = ['EquipmentId', 'DeviceID',
                     'DeviceSN', 'Description']
    reversion_enable = True


# 将Author模块和管理类绑定在一起，注册到后台管理
xadmin.site.register(Equipment_detail, Equipment_detailAdmin)


class re_versionAdmin(object):
    reversion_enable = True
    list_export = ('xls',)
    list_display = ('revision', 'object_id',
                    'content_type',
                    'serialized_data', 'object_repr')
    search_fields = ('revision', 'object_id',
                     'content_type',
                     'serialized_data', 'object_repr')
    list_filter = ('revision', 'object_id',
                   'content_type',
                   'serialized_data', 'object_repr')
    fields = ('revision',)


xadmin.site.register(Version, re_versionAdmin)








