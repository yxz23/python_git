# encoding: utf-8
from django.db import models
from django.core.exceptions import ValidationError
import os
import sys
import datetime
from .wikiManager import WikiManager

# from .sigleton import singleton
reload(sys)
sys.setdefaultencoding('utf-8')

wiki_manager = WikiManager()


class CM_Application(models.Model):
    '''记录每个应用系统的基本信息'''
    ServiceType_CHOICES = (('hexin', '核心'), ('fuzhu', '辅助'), ('qita', '其他'))
    Status_CHOICES = (('shangxian', '上线'), ('xiaxian', '下线'), ('zhanting', '暂停'))

    # EnvDesType_CHOICE = (('UAT1','UAT1'),('UAT2','UAT2'),('UAT3','UAT3'),('MEMB','MEMB'),('peixun','培训'))
    AppID = models.AutoField(primary_key=True, verbose_name='应用系统ID')
    Category = models.CharField(max_length=64, verbose_name='系统分类')
    ChineseName = models.CharField(max_length=128, verbose_name='系统中文名', unique=True)

    EnglishName = models.CharField(max_length=64, verbose_name='系统英文名')

    # EnvType = models.CharField(max_length=32,choices=EnvType_CHOICE, verbose_name = '环境类型')
    UATVersion = models.CharField(max_length=32, verbose_name='生产版本号')
    ServiceType = models.CharField(max_length=64, choices=ServiceType_CHOICES, verbose_name='系统等级')
    Status = models.CharField(max_length=64, choices=Status_CHOICES, verbose_name='状态')
    LaunchDate = models.DateField(verbose_name='上线日期')
    OffDate = models.DateField(verbose_name='下线日期', blank=True)
    ServiceStart = models.TimeField(verbose_name='服务开始时间')
    ServiceEnd = models.TimeField(verbose_name='服务结束时间')
    OperationStart = models.CharField(max_length=128, verbose_name='禁止变更时间段')
    AvailableDate = models.CharField(max_length=128, verbose_name='可用日期')
    UatRelease = models.CharField(max_length=300, verbose_name='UAT发布路径')
    ProdRelease = models.CharField(max_length=300, verbose_name='模拟发布路径')
    Description = models.CharField(max_length=500, verbose_name='系统描述')
    Remark = models.CharField(max_length=500, blank=True, verbose_name='备注')
    # UpdateDate = models.DateField(default = datetime.date.today(),verbose_name = '更新日期')
    UpdateDate = models.DateField(verbose_name='更新日期')

    def save(self, *args, **kwargs):
        super(CM_Application, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(CM_Application, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.AppID, self.ChineseName)

    class Meta:
        db_table = u"cm_vrms_wiki_cm_application"
        verbose_name = u"应用系统配置信息"
        verbose_name_plural = u"应用系统配置基本信息表"


class CM_Application_Maintainer(models.Model):
    # 记录应用配置人员的相关信息
    ID = models.AutoField(primary_key=True, verbose_name='ID')
    AppID = models.ForeignKey(CM_Application, verbose_name='应用系统ID')
    DeptName = models.CharField(max_length=64, verbose_name='业务部门')
    CMA = models.CharField(max_length=32, verbose_name='配置管理岗A')
    CMB = models.CharField(max_length=32, verbose_name='配置管理岗B')
    DeilverA = models.CharField(max_length=32, verbose_name='项目交付岗A')
    DeilverB = models.CharField(max_length=32, verbose_name='项目交付岗B')
    DevPM = models.CharField(max_length=32, verbose_name='项目经理')
    DevCompany = models.CharField(max_length=64, verbose_name='开发公司')
    DevCompanyPM = models.CharField(max_length=32, verbose_name='开发公司联系人')
    TestPM = models.CharField(max_length=32, verbose_name='第三方测试负责人')
    TestLD = models.CharField(max_length=32, verbose_name='第三方测试组长')

    def save(self, *args, **kwargs):
        super(CM_Application_Maintainer, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(CM_Application_Maintainer, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.ID)

    class Meta:
        db_table = u"cm_vrms_wiki_cm_application_maintainer"
        verbose_name = u"应用系统配置人员信息"
        verbose_name_plural = u"应用系统配置人员信息表"


class Cluser(models.Model):
    # 记录虚拟化集群信息

    CluserID = models.AutoField(primary_key=True, verbose_name='编号')
    VCenter = models.CharField(max_length=128, verbose_name='数据中心')
    CluserName = models.CharField(max_length=128, verbose_name='集群名称')

    def save(self, *args, **kwargs):
        super(Cluser, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Cluser, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.VCenter, self.CluserName)

    class Meta:
        db_table = u"cm_vrms_wiki_cluser"
        verbose_name = u"虚拟化集群"
        verbose_name_plural = u"虚拟化集群信息表"


class Device(models.Model):
    # 记录每台物理设备信息
    STATUS_CHOICES = (
    ('zaibao', '在保'), ('zaiyongguobao', '在用过保'), ('zaiyongbubao', '在用不保'), ('kufang', '库房'), ('bapfei', '报废'))
    CATEGORY_CHOICE = (('server', '服务器'), ('storage', '存储'), ('network', '网络设备'), ('equiment', '机房设备'))
    DeviceID = models.AutoField(primary_key=True, verbose_name='物理机编号')
    DeviceSN = models.CharField(max_length=128, verbose_name='物理机序列号')
    MANUFACTURER = models.CharField(max_length=64, verbose_name='生产厂商')
    CATEGORY = models.CharField(max_length=64, choices=CATEGORY_CHOICE, verbose_name='设备类别')
    PURCHASE_DATE = models.DateField(verbose_name='购置日期')
    # SERVICE_END_DATE = models.DateField(verbose_name = '维保到期日')
    # STATUS = models.CharField(max_length=32, choices=STATUS_CHOICES, verbose_name = '使用状态')
    maintainerA = models.CharField(max_length=32, verbose_name='运维A')
    maintainerB = models.CharField(max_length=32, verbose_name='运维B')
    DISTRICT = models.CharField(max_length=32, verbose_name='区域')
    ROOM = models.CharField(max_length=32, verbose_name='机房')
    CABINET = models.CharField(max_length=32, verbose_name='机柜')
    COUNT_U = models.CharField(max_length=32, verbose_name='U数')
    # AssociateDeviceid = models.ForeignKey('self', null = True,blank=True, verbose_name = '关联父设备ID')
    REMARK = models.CharField(max_length=1024, blank=True, verbose_name='功率负载')
    # UpdateTime = models.DateField(default = datetime.date.today(), verbose_name = '更新时间')
    UpdateTime = models.DateField(verbose_name='更新时间')

    def save(self, *args, **kwargs):
        super(Device, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Device, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        # return "{}\t{}\t{}".format(self.DeviceSN,self.MANUFACTURER,self.CATEGORY)
        return self.DeviceSN

    class Meta:
        db_table = u"cm_vrms_wiki_device"
        verbose_name = u"物理设备信息"
        verbose_name_plural = u"物理设备信息表"


class storage_detail(models.Model):
    # 记录每台存储的详细信息
    EXPANSIBILITY_CHOICES = (('Y', '是'), ('N', '否'))
    StorageId = models.AutoField(primary_key=True, verbose_name='存储ID')
    DeviceID = models.ForeignKey(Device, verbose_name='物理机编号')
    STORAGE_NAME = models.CharField(max_length=32, verbose_name='存储名')
    DeviceSN = models.CharField(max_length=64, verbose_name='设备序列号')
    Firmware = models.CharField(max_length=64, verbose_name='微码')
    Ctlr_NUM = models.IntegerField(verbose_name='控制器数')
    DISK_TYPE = models.CharField(max_length=32, verbose_name='DISK类型')
    DISK_Capacity = models.CharField(max_length=32, verbose_name='DISK容量')
    DISK_NUM = models.CharField(max_length=32, verbose_name='DISK数量')
    IP = models.CharField(max_length=32, verbose_name='管理IP')
    EXPANSIBILITY = models.CharField(max_length=32, choices=EXPANSIBILITY_CHOICES, verbose_name='扩展柜')

    def save(self, *args, **kwargs):
        super(storage_detail, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(storage_detail, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.StorageId, self.STORAGE_NAME)

    class Meta:
        db_table = u"cm_vrms_wiki_storage_detail"
        verbose_name = u"存储信息"
        verbose_name_plural = u"存储详细信息表"


class Appserver(models.Model):
    # 记录每个服务器的资源信息
    EnvType_CHOICE = (
    ('ST', 'ST'), ('UAT-A', 'UAT-A'), ('UAT-B', 'UAT-B'), ('UAT-C', 'UAT-C'), ('MEMB', 'MEMB'), ('peixun', '培训'))
    Usage_CHOICES = (('application', '应用'), ('db', '数据库'), ('app&db', '应用&数据库'))
    AppServerID = models.AutoField(primary_key=True, verbose_name='服务器编号')
    AppID = models.ForeignKey(CM_Application, blank=True, null=True, verbose_name='应用系统ID')
    DeviceID = models.ForeignKey(Device, blank=True, null=True, verbose_name='物理机编号')
    CluserID = models.ForeignKey(Cluser, blank=True, null=True, verbose_name='集群名称')
    HostName = models.CharField(max_length=32, verbose_name='主机名')
    LogicHostname = models.CharField(max_length=32, blank=True, verbose_name='逻辑主机名')
    OsName = models.CharField(max_length=32, verbose_name='操作系统')
    OSVersion = models.CharField(max_length=32, verbose_name='操作系统版本')
    CpuSpeed = models.CharField(max_length=32, verbose_name='CPU主频')
    CpuNum = models.IntegerField(verbose_name='CPU数量')
    MemorySize = models.IntegerField(verbose_name='内存（单位：M）')
    DiskSize = models.IntegerField(verbose_name='磁盘（单位：M）')
    LBIP = models.CharField(max_length=32, blank=True, verbose_name='负载均衡IP')
    ServiceIP = models.CharField(max_length=32, verbose_name='服务IP')
    ServerIP = models.CharField(max_length=32, blank=True, verbose_name='虚拟化集群/宿主IP')
    Usage = models.CharField(max_length=32, blank=True, choices=Usage_CHOICES, verbose_name='功能说明')
    Remark = models.CharField(max_length=1024, blank=True, choices=EnvType_CHOICE, verbose_name='环境名称',
                              help_text='描述系统环境:UATA，UATB等')
    Remark1 = models.CharField(max_length=1024, blank=True, verbose_name='UAT版本', help_text='当前环境UAT版本号')
    # UpdateTime = models.DateField(default = datetime.date.today(), verbose_name = '更新时间')
    UpdateTime = models.DateField(verbose_name='更新时间')

    def save(self, *args, **kwargs):
        super(Appserver, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Appserver, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

        '''添加到历史表'''
        print  type(self.AppID), unicode(self.AppID).split('\t')[1]
        his = AppserverHistory(
            Device=self.DeviceID,
            Application=unicode(self.AppID).split('\t')[1],
            HostName=self.HostName,
            OSVersion=self.OSVersion,
            ServiceIP=self.ServiceIP
        )
        his.save()

    def __unicode__(self):
        return "{}\t{}\t{}".format(self.AppServerID, self.HostName, self.AppID)

    class Meta:
        # unique_together = ("HostName", "ServiceIP")
        db_table = u"cm_vrms_wiki_appserver"
        verbose_name = u"服务器资源信息"
        verbose_name_plural = u"服务器资源信息表"


class AppserverHistory(models.Model):
    '''记录已删除服务器的资源信息'''
    Device = models.CharField(max_length=128, blank=True, null=True, verbose_name='物理机编号')
    Application = models.CharField(max_length=128, blank=True, null=True, verbose_name='应用系统')
    HostName = models.CharField(max_length=32, blank=True, null=True, verbose_name='主机名')
    OSVersion = models.CharField(max_length=32, blank=True, null=True, verbose_name='操作系统版本')
    ServiceIP = models.CharField(max_length=32, blank=True, null=True, verbose_name='服务IP')
    DeleteTime = models.DateField(default=datetime.date.today(), verbose_name='删除时间')

    def __unicode__(self):
        return "{}\t{}\t{}".format(self.Device, self.Application, self.HostName)

    class Meta:
        db_table = u"cm_vrms_wiki_appserver_history"
        verbose_name = u"服务器资源信息历史表"
        verbose_name_plural = u"服务器资源信息历史表"


class Mount(models.Model):
    # 记录应用服务器外接存储挂载信息
    MountID = models.AutoField(primary_key=True, verbose_name='挂载点ID')
    StorageDeviceId = models.ForeignKey(storage_detail, verbose_name='存储ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    MountPath = models.CharField(max_length=128, verbose_name='外接存储挂载点')

    def save(self, *args, **kwargs):
        super(Mount, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Mount, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.MountPath)

    class Meta:
        db_table = u"cm_vrms_wiki_mount"
        verbose_name = u"存储挂载点信息"
        verbose_name_plural = u"存储挂载点信息"


class LB(models.Model):
    # 记录应用服务器集群信息
    LBID = models.AutoField(primary_key=True, verbose_name='负载均衡ID')
    AppID = models.ForeignKey(CM_Application, verbose_name='应用系统ID')
    LBName = models.CharField(max_length=64, verbose_name='负载均衡名称')
    LBIP = models.CharField(max_length=32, verbose_name='负载均衡IP')

    def save(self, *args, **kwargs):
        super(LB, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(LB, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.LBID, self.LBName)

    class Meta:
        db_table = u"cm_vrms_wiki_lb"
        verbose_name = u"应用服务器集群信息"
        verbose_name_plural = u"应用服务器集群信息"


class LB_Member(models.Model):
    # 记录应用服务器组员信息
    LBID = models.ForeignKey(LB, verbose_name='负载均衡ID')
    AppID = models.ForeignKey(CM_Application, verbose_name='应用系统ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    AppServerIP = models.CharField(max_length=64, verbose_name='服务器IP')

    def save(self, *args, **kwargs):
        super(LB_Member, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(LB_Member, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}\t{}\t{}".format(self.LBID, self.AppID, self.AppServerID, self.AppServerIP)

    class Meta:
        db_table = u"cm_vrms_wiki_lb_member"
        verbose_name = u"应用服务器组员信息"
        verbose_name_plural = u"应用服务器组员信息"


class CM_Users(models.Model):
    # 记录每台服务器的用户信息
    UserType_CHOICES = (('application', '应用用户'), ('db', '数据库用户'), ('app&db', '应用&数据库用户'))
    UserID = models.AutoField(primary_key=True, verbose_name='用户ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    UserName = models.CharField(max_length=32, verbose_name='用户名')
    UserType = models.CharField(max_length=32, choices=UserType_CHOICES, verbose_name='用户类别')
    ExpirationDate = models.DateField(verbose_name='用户到期时间', help_text='永不到期，用“9999-12-31”表示')
    PGroupName = models.CharField(max_length=32, verbose_name='主组')
    SGroupName = models.CharField(max_length=64, verbose_name='附属组', blank=True)

    def save(self, *args, **kwargs):
        super(CM_Users, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(CM_Users, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.UserID, self.UserName)

    class Meta:
        db_table = u"cm_vrms_wiki_cm_users"
        verbose_name = u"系统用户信息"
        verbose_name_plural = u"系统用户信息表"


class Config_File(models.Model):
    # 记录每台服务器重要配置文件的详细信息
    ConfigId = models.AutoField(primary_key=True, verbose_name='配置ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    ConfigName = models.CharField(max_length=256, verbose_name='应用配置文件名')
    UserID = models.ForeignKey(CM_Users, to_field='UserID', verbose_name='用户ID')
    ConfigDescription = models.CharField(max_length=2048, blank=True, verbose_name='参数说明')

    def save(self, *args, **kwargs):
        super(Config_File, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Config_File, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}\t{}".format(self.ConfigId, self.AppServerID, self.ConfigName)

    class Meta:
        db_table = u"cm_vrms_wiki_config_file"
        verbose_name = u"服务器配置信息"
        verbose_name_plural = u"服务器配置信息表"


class Log_File(models.Model):
    # 记录每台服务器日志的详细信息
    LogId = models.AutoField(primary_key=True, verbose_name='日志ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    UserID = models.ForeignKey(CM_Users, to_field='UserID', verbose_name='用户ID')
    LogPath = models.CharField(max_length=256, verbose_name='日志所在目录')
    LogDescription = models.CharField(max_length=256, blank=True, verbose_name='日志内容说明')
    LifeCycle = models.CharField(max_length=512, blank=True, verbose_name='定期维护说明')

    def save(self, *args, **kwargs):
        super(Log_File, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Log_File, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.LogId)

    class Meta:
        db_table = u"cm_vrms_wiki_log_file"
        verbose_name = u"服务器日志信息"
        verbose_name_plural = u"服务器日志信息表"


class Server_Process_Pool(models.Model):
    # 记录每台服务器进程端口详细信息
    ProcessId = models.AutoField(primary_key=True, verbose_name='进程ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    UserID = models.ForeignKey(CM_Users, to_field='UserID', verbose_name='用户ID')
    ProcessName = models.CharField(max_length=64, verbose_name='进程名')
    Port = models.IntegerField(verbose_name='端口号')
    Function = models.CharField(max_length=256, blank=True, verbose_name='功能说明')

    def save(self, *args, **kwargs):
        super(Server_Process_Pool, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Server_Process_Pool, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.ProcessId, self.ProcessName)

    class Meta:
        db_table = u"cm_vrms_wiki_server_process_pool"
        verbose_name = u"服务器进程信息"
        verbose_name_plural = u"服务器进程信息表"


class Software(models.Model):
    # 记录软件的信息
    SoftwareType_CHOICES = (
    ('weblogic', 'weblogic'), ('DB', 'DB'), ('MQ', 'MQ'), ('Tomcat', 'Tomcat'), ('Appache', 'Appache'),
    ('Other', 'Other'))
    SoftwareID = models.AutoField(primary_key=True, verbose_name='软件ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    SoftwareType = models.CharField(max_length=24, choices=SoftwareType_CHOICES, verbose_name='软件类型')
    SoftwareName = models.CharField(max_length=32, verbose_name='软件名')
    InstallPath = models.CharField(max_length=256, verbose_name='安装路径')
    Version = models.CharField(max_length=32, verbose_name='版本号')

    def save(self, *args, **kwargs):
        super(Software, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Software, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}\t{}".format(self.SoftwareID, self.SoftwareType, self.SoftwareName)

    class Meta:
        db_table = u"cm_vrms_wiki_software"
        verbose_name = u"软件信息"
        verbose_name_plural = u"软件信息表"


class Weblogic(models.Model):
    # 记录weblogic的详细信息
    WeblogicID = models.AutoField(primary_key=True, verbose_name='WeblogicID')
    SoftwareID = models.ForeignKey(Software, verbose_name='软件ID')
    ConsoleContexPath = models.CharField(max_length=128, verbose_name='控制台路径')
    ConsoleUserName = models.CharField(max_length=24, verbose_name='控制台账号')
    DomianName = models.CharField(max_length=32, verbose_name='域名')
    DomainPath = models.CharField(max_length=128, verbose_name='域路径')
    WeblogicServerName = models.CharField(max_length=32, verbose_name='WeblogicServer名')
    Listener = models.CharField(max_length=32, verbose_name='监听端口')
    SSLListener = models.CharField(max_length=32, verbose_name='SSL监听端口')
    JDBCType = models.CharField(max_length=64, verbose_name='JDBC类型')
    JNDIName = models.CharField(max_length=64, verbose_name='JNDI名')
    JDBCUrl = models.CharField(max_length=64, verbose_name='JDBCUrl')
    Driver = models.CharField(max_length=64, verbose_name='驱动名称')

    def save(self, *args, **kwargs):
        super(Weblogic, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Weblogic, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.WeblogicID)

    class Meta:
        db_table = u"cm_vrms_wiki_weblogic"
        verbose_name = u"weblogic信息"
        verbose_name_plural = u"weblogic信息表"


class Weblogic_Jdbc(models.Model):
    # 记录JDBC的详细信息
    JdbcID = models.AutoField(primary_key=True, verbose_name='JDBCID')
    WeblogicID = models.ForeignKey(Weblogic, verbose_name='WeblogicID')
    JDBCType = models.CharField(max_length=64, verbose_name='JDBC类型')
    JNDIName = models.CharField(max_length=64, verbose_name='JNDI名')
    JDBCUrl = models.CharField(max_length=64, verbose_name='JDBCUrl')
    Driver = models.CharField(max_length=64, verbose_name='驱动名称')

    def save(self, *args, **kwargs):
        super(Weblogic_Jdbc, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Weblogic_Jdbc, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.JdbcID, self.WeblogicID)

    class Meta:
        db_table = u"cm_vrms_wiki_weblogic_jdbc"
        verbose_name = u"weblogic_JDBC信息"
        verbose_name_plural = u"weblogic_JDBC信息表"


class Weblogic_Server(models.Model):
    # 记录Weblogic_Server的详细信息
    ServerID = models.AutoField(primary_key=True, verbose_name='ServerID')
    WeblogicID = models.ForeignKey(Weblogic, verbose_name='WeblogicID')
    WeblogicServerName = models.CharField(max_length=32, verbose_name='WeblogicServer名')
    Listener = models.CharField(max_length=32, verbose_name='监听端口')
    SSLListener = models.CharField(max_length=32, verbose_name='SSL监听端口')

    def save(self, *args, **kwargs):
        super(Weblogic_Server, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Weblogic_Server, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}\t{}".format(self.ServerID, self.WeblogicID, self.WeblogicServerName)

    class Meta:
        db_table = u"cm_vrms_wiki_weblogic_server"
        verbose_name = u"weblogic_server信息"
        verbose_name_plural = u"weblogic_server信息表"


class Weblogic_Jdbc_Map(models.Model):
    # 记录WeblogicJDBC映射信息
    ServerID = models.ForeignKey(Weblogic_Server, verbose_name='ServerID')
    JdbcID = models.ForeignKey(Weblogic_Jdbc, verbose_name='JDBCID')

    def save(self, *args, **kwargs):
        super(Weblogic_Jdbc_Map, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Weblogic_Jdbc_Map, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.ServerID, self.JdbcID)

    class Meta:
        db_table = u"cm_vrms_wiki_weblogic_jdbc_map"
        verbose_name = u"weblogic_jdbc映射信息"
        verbose_name_plural = u"weblogic_jdbc映射信息表"


class Weblogic_App(models.Model):
    # 记录Weblogic_App应用部署信息
    AppID = models.AutoField(primary_key=True, verbose_name='AppID')
    ServerID = models.ForeignKey(Weblogic_Server, verbose_name='ServerID')
    AppName = models.CharField(max_length=32, verbose_name='WebApp名')
    DeployPath = models.CharField(max_length=128, verbose_name='WebApp部署路径')
    DeployType = models.CharField(max_length=32, verbose_name='部署类型')
    Description = models.CharField(max_length=256, blank=True, verbose_name='描述信息')

    def save(self, *args, **kwargs):
        super(Weblogic_App, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Weblogic_App, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.AppID, self.AppName)

    class Meta:
        db_table = u"cm_vrms_wiki_weblogic_app"
        verbose_name = u"weblogic应用部署信息"
        verbose_name_plural = u"weblogic应用部署信息表"


class License(models.Model):
    # license的详细信息
    LicenseID = models.AutoField(primary_key=True, verbose_name='LicenseID')
    AppID = models.ForeignKey(CM_Application, verbose_name='应用系统ID')
    AppServerID = models.ForeignKey(Appserver, verbose_name='服务器编号')
    Software = models.CharField(max_length=256, verbose_name='软件名称')
    Version = models.CharField(max_length=32, verbose_name='版本')
    DueDate = models.DateField(verbose_name='到期日')
    Company = models.CharField(max_length=64, verbose_name='厂商')
    Remark = models.CharField(max_length=128, blank=True, verbose_name='备注')

    def save(self, *args, **kwargs):
        super(License, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(License, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}\t{}\t{}".format(self.LicenseID, self.AppID, self.AppServerID, self.Software)

    class Meta:
        db_table = u"cm_vrms_wiki_license"
        verbose_name = u"许可证信息"
        verbose_name_plural = u"许可证信息"


class DB(models.Model):
    # 数据的详细信息
    HA_CHOICES = (('Y', '是'), ('N', '否'))
    DBID = models.AutoField(primary_key=True, verbose_name='DBID')
    SoftwareID = models.ForeignKey(Software, verbose_name='软件ID')
    INSTANCE_NAME = models.CharField(max_length=32, verbose_name='实例名')
    DBName = models.CharField(max_length=32, verbose_name='数据库名')
    DataFile = models.CharField(max_length=128, verbose_name='数据文件路径', blank=True)
    LogFile = models.CharField(max_length=128, verbose_name='日志文件路径', blank=True)
    Port = models.CharField(max_length=32, verbose_name='监听端口')
    DbUser = models.CharField(max_length=32, verbose_name='数据库用户')
    HA = models.CharField(max_length=32, choices=HA_CHOICES, verbose_name='高可用模式')
    MEMBER = models.CharField(max_length=128, verbose_name='组员')

    def save(self, *args, **kwargs):
        super(DB, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(DB, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.DBID)

    class Meta:
        db_table = u"cm_vrms_wiki_db"
        verbose_name = u"数据库信息"
        verbose_name_plural = u"数据库信息表"


class MQ(models.Model):
    # MQ的详细信息
    MQID = models.AutoField(primary_key=True, verbose_name='MQID')
    SoftwareID = models.ForeignKey(Software, verbose_name='软件ID')
    QueueManager = models.CharField(max_length=32, verbose_name='队列管理器名')
    QLocal = models.CharField(max_length=32, verbose_name='本地队列名')
    QRemote = models.CharField(max_length=32, verbose_name='远程队列名')
    Chanel = models.CharField(max_length=32, verbose_name='通道')
    Port = models.IntegerField(verbose_name='端口')

    def save(self, *args, **kwargs):
        super(MQ, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(MQ, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.MQID)

    class Meta:
        db_table = u"cm_vrms_wiki_mq"
        verbose_name = u"消息队列（MQ）信息"
        verbose_name_plural = u"消息队列（MQ）信息表"


class Tomcat(models.Model):
    # Tomcat详细信息
    TomcatID = models.AutoField(primary_key=True, verbose_name='TomcatID')
    SoftwareID = models.ForeignKey(Software, verbose_name='软件ID')
    Port = models.IntegerField(verbose_name='监听端口')
    SSLPort = models.IntegerField(verbose_name='SSL监听端口')
    DocmentRoot = models.CharField(max_length=128, verbose_name='DocmentRoot')

    def save(self, *args, **kwargs):
        super(Tomcat, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Tomcat, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.TomcatID)

    class Meta:
        db_table = u"cm_vrms_wiki_tomcat"
        verbose_name = u"Tomcat信息"
        verbose_name_plural = u"Tomcat信息表"


class Apache(models.Model):
    ApacheID = models.AutoField(primary_key=True, verbose_name='ApacheID')
    SoftwareID = models.ForeignKey(Software, verbose_name='软件ID')
    Port = models.IntegerField(verbose_name='监听端口')
    SSLPort = models.IntegerField(verbose_name='SSL监听端口')
    DocmentRoot = models.CharField(max_length=128, verbose_name='DocmentRoot')

    def save(self, *args, **kwargs):
        super(Apache, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Apache, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.ApacheID)

    class Meta:
        db_table = u"cm_vrms_wiki_apache"
        verbose_name = u"Apache信息"
        verbose_name_plural = u"Apache信息表"


class Other(models.Model):
    OtherID = models.AutoField(primary_key=True, verbose_name='OtherID')
    SoftwareID = models.ForeignKey(Software, verbose_name='软件ID')
    Description = models.CharField(max_length=1024, verbose_name='描述')

    def save(self, *args, **kwargs):
        super(Other, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Other, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.OtherID)

    class Meta:
        db_table = u"cm_vrms_wiki_other"
        verbose_name = u"其他应用信息"
        verbose_name_plural = u"其他应用信息表"


class server_detail(models.Model):
    # 记录每台服务器的详细信息
    CPU_TYPE_CHOICES = (('pcserver', 'pc服务器'), ('xiaoxinji', '小型机'))
    ServerId = models.AutoField(primary_key=True, verbose_name='服务器ID')
    DeviceID = models.ForeignKey(Device, verbose_name='物理机编号')
    ServerName = models.CharField(max_length=64, verbose_name='设备名')
    DeviceSN = models.CharField(max_length=64, verbose_name='设备序列号', unique=True)
    Server_type = models.CharField(max_length=64, choices=CPU_TYPE_CHOICES, verbose_name='服务器类型')
    CPU_TYPE = models.CharField(max_length=32, verbose_name='cpu型号')
    CPU_FREQUENCY = models.CharField(max_length=32, verbose_name='cpu核心频率')
    CPU_NUM = models.IntegerField(verbose_name='CPU物理个数')
    CPU_CORE_NUM = models.IntegerField(verbose_name='总物理CPU核心数')
    MEM_TYPE = models.CharField(max_length=32, verbose_name='内存型号')
    MEM_CONF = models.CharField(max_length=1024, verbose_name='内存组成', help_text='格式：1G*2+2G*2，表示容量*数量')
    MEM_SIZE = models.CharField(max_length=32, verbose_name='内存可用容量')
    HARDDISK_CAPACITY = models.CharField(max_length=1024, verbose_name='硬盘组成',
                                         help_text='格式：146G*2（RAID1）+300G*2（RAID1），表示容量*数量(RAID)')
    DISK_SIZE = models.CharField(max_length=32, verbose_name='硬盘可用容量')
    NETWORK_CARD = models.CharField(max_length=1024, verbose_name='网卡组成')
    HBACARD = models.CharField(max_length=1024, verbose_name='光纤卡组成')

    def save(self, *args, **kwargs):
        super(server_detail, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(server_detail, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}\t{}".format(self.ServerId, self.ServerName)

    class Meta:
        db_table = u"cm_vrms_wiki_server_detail"
        verbose_name = u"服务器详细信息"
        verbose_name_plural = u"服务器详细信息表"


class NetDevice_detail(models.Model):
    # 记录每台网络设备的详细信息
    NetDeviceId = models.AutoField(primary_key=True, verbose_name='设备ID')
    DeviceID = models.ForeignKey(Device, verbose_name='物理机编号')
    DeviceSN = models.CharField(max_length=64, verbose_name='设备序列号')
    NetDeviceType = models.CharField(max_length=64, verbose_name='设备序类型')
    MANAGE_IP = models.CharField(max_length=32, verbose_name='管理地址')
    IOS_VERSION = models.CharField(max_length=32, verbose_name='IOS版本')

    def save(self, *args, **kwargs):
        super(NetDevice_detail, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(NetDevice_detail, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.NetDeviceId)

    class Meta:
        db_table = u"cm_vrms_wiki_netdevice_detail"
        verbose_name = u"网络设备信息"
        verbose_name_plural = u"网络设备详细信息表"


class Equipment_detail(models.Model):
    # 记录机房其他的详细信息
    EquipmentId = models.AutoField(primary_key=True, verbose_name='设备ID')
    DeviceID = models.ForeignKey(Device, verbose_name='物理机编号')
    DeviceSN = models.CharField(max_length=64, verbose_name='设备序列号')
    Description = models.CharField(max_length=1024, blank=True, verbose_name='描述')

    def save(self, *args, **kwargs):
        super(Equipment_detail, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Equipment_detail, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.EquipmentId)

    class Meta:
        db_table = u"cm_vrms_wiki_equipment_detail"
        verbose_name = u"机房其他设备信息"
        verbose_name_plural = u"机房其他设备信息表"


class Config_Item(models.Model):
    # 记录每台服务器配置文件中的配置项详细信息
    ConfigItemId = models.AutoField(primary_key=True, verbose_name='配置项ID')
    ConfigName = models.ForeignKey(Config_File, verbose_name='应用配置文件名')
    Parameter = models.CharField(max_length=256, verbose_name='配置项')
    value = models.CharField(max_length=256, verbose_name='配置值')
    bl1 = models.BooleanField(verbose_name='同一版本不同环境是否相同')
    bl2 = models.BooleanField(verbose_name='不同版本相同环境是否相同')
    ConfigDescription = models.CharField(max_length=2048, blank=True, verbose_name='参数说明')

    def save(self, *args, **kwargs):
        super(Config_Item, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(Config_Item, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.ConfigItemId)

    class Meta:
        db_table = u"cm_vrms_wiki_config_item"
        verbose_name = u"服务器配置项信息"
        verbose_name_plural = u"服务器配置项信息表"


class ImageStore(models.Model):
    AppID = models.ForeignKey(CM_Application, verbose_name='应用系统ID')
    name = models.CharField(max_length=150, null=True)
    img = models.ImageField(upload_to='img')

    def save(self, *args, **kwargs):
        super(ImageStore, self).save(*args, **kwargs)
        wiki_manager.set_changed(True)

    def delete(self, *args, **kwargs):
        super(ImageStore, self).delete(*args, **kwargs)
        wiki_manager.set_changed(True)

    def __unicode__(self):
        return "{}".format(self.name)

    class Meta:
        db_table = u"cm_vrms_wiki_image_store"
        verbose_name = u"服务器架构图"
        verbose_name_plural = u"服务器架构图表"



