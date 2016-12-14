# encoding: utf-8
from django.db import models
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import copy
import xlrd
import datetime
import time
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from cm_vrms_upload.settings import UPLOAD_FILE_PATH


def singleton(cls, *args, **kw):
    '''单例实现'''  
    instances = {}  
    def _singleton():  
        if cls not in instances:  
            instances[cls] = cls(*args, **kw)  
        return instances[cls]  
    return _singleton  


def convert_xlsx_csv(xlsx_path,csv_path):
    '''通用函数,解析xlsx文件,转为csv.后续更新到class中'''
    wb = xlrd.open_workbook(xlsx_path) 
    sheet_name = wb.sheet_names()[0]
    sh = wb.sheet_by_name(sheet_name) 
    your_csv_file = open(csv_path, 'wb+')
    for rownum in xrange(sh.nrows):
        line_values = sh.row_values(rownum)
        line_types = sh.row_types(rownum)
        for i in range(0,len(line_types)):
            if line_types[i] == 3:
                try:
                #line_values[i] = "{}-{}-{}".format(*xlrd.xldate_as_tuple(line_values[i],wb.datemode))
                    year,month,day=xlrd.xldate_as_tuple(line_values[i],wb.datemode)[:3]
                    tmp_date = datetime.date(year,month,day)
                    line_values[i] = tmp_date.strftime('%Y-%m-%d')
                except:
                    line_values[i] = ""
                
        line_values = [str(val) for val in line_values]
        line_str = "\t".join(line_values)
        line_str = line_str.replace("\r\n", "")
        line_str = line_str.replace("\n", "")
        line_str = line_str.replace("(", "（")
        line_str = line_str.replace(")", "）")
        line_str = line_str.encode("utf-8")
        your_csv_file.write(line_str+"\n")
    your_csv_file.close()
    

def convert_csv_csv(file_path,csv_path):#转gbk的csv为utf-8的
    fout = open(csv_path,"wb+")

    with open(file_path) as source_file:
        for line in source_file.xreadlines():
            line = line.strip()
            line_str = line.decode("gbk").encode("utf-8")
            line_str = "\t".join(line_str.split(","))
            fout.write(line_str + "\n")

    fout.close()
    

class NameMap(models.Model):
    rawname=models.CharField(max_length=500, verbose_name = '原始名')
    mapname=models.CharField(max_length=500, verbose_name = '映射名' )
    def save(self, *args, **kwargs):
        '''重写保存方法'''
        super(NameMap, self).save(*args, **kwargs) # Call the "real" save() method.
        tmp_info = NamemapInfo()#更新namemap_info
        tmp_info.refresh_sys_info()
    
    def delete(self, *args, **kwargs):
        #重写删除方法
        super(NameMap, self).delete(*args, **kwargs) # Call the "real" delete() method.
        tmp_info = NamemapInfo()#更新sys_info
        tmp_info.refresh_sys_info()      
    def __unicode__(self):
        return '''{0}\t{1}'''.format(self.rawname,
                         self.mapname)
        
    class Meta:
        db_table = u"namemap"
        verbose_name=u"系统名称映射表"
        verbose_name_plural=u"系统名称映射表(总)"
        
        
@singleton
class NamemapInfo(object):
    '''namemap_info 即为名称映射信息'''
    
    def __init__(self):
        self.namemap_info = {}
        self.namemap_info = self.read_conf_info_from_db()
    
    def refresh_sys_info(self):
        #更新namemap信息
        self.namemap_info = self.read_conf_info_from_db()
        return self.namemap_info
            
    def read_conf_info_from_db(self):
        '''从数据库中读取namemap_info'''
        conf_info_list = NameMap.objects.all()
        namemap_info = {}
        for conf_info in conf_info_list:
            try:
                rawname=conf_info.rawname.encode("utf-8")
                mapname=conf_info.mapname.encode("utf-8")
                namemap_info[rawname] = mapname
            except:
                print conf_info
        return namemap_info
   

def convert_name(name):#如果在映射内,则返回映射后结果。否则返回原字符串
    try:
        namemap_info = NamemapInfo().namemap_info
        if name in namemap_info:
            return namemap_info[name]
        else:
            return name
    except:
        return name
    

'''测试周报中标准系统名称表'''
class SysName_Info(models.Model):
    SysName = models.CharField(max_length=256, verbose_name = '系统名称')
    map_sysname = models.CharField(max_length=256, verbose_name = '映射系统名称')
    
    def save(self, *args, **kwargs):
        '''重写保存方法'''
        super(SysName_Info, self).save(*args, **kwargs) # Call the "real" save() method.
        tmp_info = SysNameInfo()#更新sys_info
        tmp_info.refresh_sys_info()
    
    def delete(self, *args, **kwargs):
        #重写删除方法
        super(SysName_Info, self).delete(*args, **kwargs) # Call the "real" delete() method.
        tmp_info = SysNameInfo()#更新sys_info
        tmp_info.refresh_sys_info() 
    
    def __unicode__(self):
        return "{0}\t{1}".format(self.SysName,self.map_sysname)
    class Meta:
        db_table = u"test_report_Sys_Name"
        verbose_name=u"测试周报系统名称表"
        verbose_name_plural=u"测试周报系统名称表"
        
@singleton
class SysNameInfo(object):
    '''SysNameInfo 即为测试管理周报中系统标准命名信息'''
    
    def __init__(self):
        self.sys_info = {}
        self.sys_info = self.read_conf_info_from_db()
    
    def refresh_sys_info(self):
        #更新信息
        self.sys_info = self.read_conf_info_from_db()
        return self.sys_info
    
    def update_conf_from_file(self,request,filename="SysName_conf.xlsx"):
        #上传文件后触发,更新文件且插入数据库
        file_path = UPLOAD_FILE_PATH
        in_path = file_path + "/media/pictures/"
        upload_file_path=in_path+filename#上传文件的地址
        user_name = request.user.username
        upload_time = time.strftime('%Y%m%d%H%M', time.localtime())
        csv_path = "{}SysName_conf_{}_{}_{}.csv".format(in_path, filename.split(".")[0], user_name, upload_time)
        csv_path = csv_path.decode("utf-8").encode("gbk")

        if ".xls" in filename:
            #xlsx_path= in_path+filename+".xlsx"#system_conf.xlsx/version.xlsx/SysName_conf.xlsx
            #将上传进来的配置文件改为csv文件,并且改成utf-8的格式
            convert_xlsx_csv(upload_file_path,csv_path)
        elif ".csv" in filename:
            convert_csv_csv(upload_file_path,csv_path)#将gbk修正为utf-8
        self.write_conf_info_to_db(request,csv_path)#插入数据库
        self.refresh_sys_info()#更新sysinfo
        
        
    def write_conf_info_to_db(self,request,file_path):
        '''将信息从文件更新到数据库中'''
        f_info = open(file_path)
        f_info.readline()  # 舍弃第一行表头（列名）
        sys_info = (val.strip().split('\t') for val in f_info.readlines())
        f_info.close()
        
        for node_info in sys_info:
            if len(node_info) != 2:
                continue

            node_info[0] = node_info[0].replace("(", "（")
            node_info[0] = node_info[0].replace(")", "）")
            try:
                conf_info_tmp = SysName_Info.objects.get(SysName=node_info[0],map_sysname=node_info[1])
                
                #若存在，则不更新
                #conf_info_tmp.save()#更新
            except SysName_Info.DoesNotExist:
                try:
                    conf_info_tmp = SysName_Info(SysName=node_info[0],map_sysname=node_info[1])
                    conf_info_tmp.save()#插入
                    
                except:
                    print "\t".join(node_info)
                
        return True  
    def read_conf_info_from_db(self):
        '''从数据库中读取SysName_Info'''
        conf_info_list = SysName_Info.objects.all()
        sys_source_node_info = {}
        for conf_info in conf_info_list:
            try:
                SysName=conf_info.SysName.encode("utf-8")
                map_sysname = conf_info.map_sysname.encode("utf-8")
                
                
                if SysName not in sys_source_node_info:
                    sys_source_node_info[SysName]=[]

                sys_source_node_info[SysName].append('''{0}'''.format(map_sysname))
            
            except:
                print "error"
                       
        return sys_source_node_info

name_info = SysName_Info.objects.all()
'''测试管理模块表信息模型'''   
class Report_Detail(models.Model):
    
    name_map={}
    for val in name_info:
        raw_name=val.SysName.encode("utf-8")
        map_name=val.map_sysname.encode("utf-8")
        name_map[map_name]=raw_name
    Name_CHOICE = tuple(sorted(name_map.iteritems(), key = lambda asd:asd[0]))
    TestType_CHOICES = (('zxt','主系统'),('sjlc','升级联测'),('wyxlc','无影响联测'),('whf','未回复'))
    ProjectStage_CHOICES = (('cszb','测试准备'),('uat1cs','UAT1测试'),('uat1wc','UAT1完成'),('yslc','验收流程'),('yslc','验收流程'),('yscs','验收测试'),('mnlc','模拟流程'),('mncs','模拟测试'),('mnwc','模拟完成'),('ysx','已上线'),('NA','NA'))
    OverallSchedule_CHOICES = (('zc','正常'),('yq','延期'),('zt','暂停'),('zf','作废'),('NA','NA'))
    ManpowerInput_CHOICES = (('rljz','人力紧张'),('rlcz','人力充足'),('rlbz','人力不足'),('NA','NA'))
    VersionQuality_CHOICES = (('zlyb','质量一般'),('zljh','质量较好'),('zljc','质量较差'),('NA','NA'))
    Workload_CHOICES = (('cqb','超签报'),('zc','正常'),('ccg','超采购'),('NA','NA'))
    TestRuns_CHOICES =(('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'))
    CRType_CHOICES =(('zc','正常'),('jj','紧急'),('lx','例行'),('kj','快捷'),('NA','NA'))
    PerformanceTest_CHOICES =(('y','有'),('n','无'))
    
    SystemName = models.CharField(max_length=128,choices=Name_CHOICE,verbose_name = '系统名称')
    VersionNum = models.CharField(max_length=64,verbose_name = '版本号')
    Main_SysName = models.CharField(max_length=128,choices=Name_CHOICE,verbose_name = '主系统名称')
    Main_VersionNum = models.CharField(max_length=64,verbose_name='主系统版本号')
    ProjectName = models.CharField(max_length=128,blank=True,verbose_name='项目名称')
    PlanTime = models.DateField(blank = True,verbose_name = '生产上线日期')
    CRType = models.CharField(max_length=32,choices=CRType_CHOICES,verbose_name = '变更类型',default ='zc')
    TestType = models.CharField(max_length=32, choices=TestType_CHOICES, verbose_name = '联测类别')
    ProjectStage = models.CharField(max_length=32, choices=ProjectStage_CHOICES, verbose_name = '目前项目阶段')
    TestRuns = models.CharField(max_length=32,choices=TestRuns_CHOICES,blank=True,verbose_name='测试轮次')
    OverallSchedule = models.CharField(max_length=32,choices=OverallSchedule_CHOICES,verbose_name='项目整体进度')
    Reason = models.TextField(max_length=2048,blank=True,verbose_name = '原因说明')
    ManpowerInput = models.CharField(max_length=32,choices=ManpowerInput_CHOICES,verbose_name = '人力投入情况')
    VersionQuality = models.CharField(max_length=32,choices=VersionQuality_CHOICES,verbose_name = '版本质量')
    Workload = models.CharField(max_length=32,choices=Workload_CHOICES,verbose_name = '工作量情况')
    PerformanceTest = models.CharField(max_length=32,choices=PerformanceTest_CHOICES,verbose_name = '性能测试')
    Writter = models.CharField(max_length=32,blank=True,verbose_name = '测试负责人')
    UpdateDate = models.DateField(default = datetime.datetime.now().date(),blank=True,verbose_name='填写日期')
    
    def save(self, *args, **kwargs):
        '''重写保存方法'''
        self.Reason = self.Reason.replace('\t', '  ')#去掉文本中的‘\t’字符
        super(Report_Detail, self).save(*args, **kwargs) # Call the "real" save() method.
        tmp_info = Report_DetailInfo()#更新sys_info
        tmp_info.refresh_sys_info()
    
    def delete(self, *args, **kwargs):
        #重写删除方法
        super(Report_Detail, self).delete(*args, **kwargs) # Call the "real" delete() method.
        tmp_info = Report_DetailInfo()#更新sys_info
        tmp_info.refresh_sys_info()
    
    def __unicode__(self):
        return "{}".format(self.SystemName)
    class Meta:
        db_table = u"test_report_Report_Detail"
        unique_together = ("SystemName", "VersionNum","Main_SysName","Main_VersionNum")
        verbose_name=u"测试周报信息"
        verbose_name_plural=u"测试周报信息表"
        
@singleton
class Report_DetailInfo(object):
    '''Report_DetailInfo 即为测试管理周报中的详细信息'''
    
    def __init__(self):
        self.sys_info = {}
        self.sys_info = self.read_conf_info_from_db()
    
    def refresh_sys_info(self):
        #更新信息
        self.sys_info = self.read_conf_info_from_db()
        return self.sys_info
    
    def update_conf_from_file(self,request,filename="Report_Detail_conf.xlsx"):
        #上传文件后触发,更新文件且插入数据库
        file_path = UPLOAD_FILE_PATH
        in_path = file_path + "/media/pictures/"
        upload_file_path = in_path + filename  # 上传文件的地址
        user_name = request.user.username
        upload_time = time.strftime('%Y%m%d%H%M', time.localtime())
        csv_path = "{}Report_Detail_conf_{}_{}_{}.csv".format(in_path, filename.split(".")[0], user_name, upload_time)
        csv_path = csv_path.decode("utf-8").encode("gbk")

        if ".xls" in filename:
            #xlsx_path= in_path+filename+".xlsx"#system_conf.xlsx/version.xlsx/SysName_conf.xlsx/Report_Detail_conf.xlsx
            #将上传进来的配置文件改为csv文件,并且改成utf-8的格式
            convert_xlsx_csv(upload_file_path,csv_path)
        elif ".csv" in filename:
            convert_csv_csv(upload_file_path,csv_path)#将gbk修正为utf-8
        self.write_conf_info_to_db(request,csv_path)#插入数据库
        self.refresh_sys_info()#更新sysinfo
        
        
    def write_conf_info_to_db(self,request,file_path):
        '''将信息从文件更新到数据库中'''
        name_map_dict={}
        for val in name_info:
            raw_name=val.SysName.encode("utf-8")
            map_name=val.map_sysname.encode("utf-8")
            name_map_dict[raw_name]=map_name
        test_type_map_info = {'主系统':'zxt','升级联测':'sjlc','无影响联测':'wyxlc','未回复':'whf','空':''}
        ProjectStage_map_info = {'测试准备':'cszb','UAT1测试':'uat1cs','UAT1完成':'uat1wc','验收流程':'yslc','验收测试':'yscs','模拟流程':'mnlc','模拟测试':'mncs','模拟完成':'mnwc','已上线':'ysx','空':'','NA':'NA'}
        OverallSchedule_map_info = {'正常':'zc','延期':'yq','暂停':'zt','作废':'zf','NA':'NA','空':''}
        ManpowerInput_map_info = {'人力紧张':'rljz','人力充足':'rlcz','人力不足':'rlbz','空':'','NA':'NA'}
        VersionQuality_map_info = {'质量一般':'zlyb','质量较好':'zljh','质量较差':'zljc','空':'','NA':'NA'}
        Workload_map_info = {'超签报':'cqb','正常':'zc','超采购':'ccg','空':'','NA':'NA'}
        CRType_map_info = {'正常':'zc','紧急':'jj','例行':'lx','快捷':'kj','空':'','NA':'NA'}
        PerformanceTest_map_info = {'有':'y','无':'n','空':''}

        f_info = open(file_path)
        f_info.readline()  # 舍弃第一行表头（列名）
        sys_info = (val.strip().split('\t') for val in f_info.readlines())
        f_info.close()
        
        for node_info in sys_info:
            systemname = node_info[0]
            node_info[0]=name_map_dict.get(systemname,"")
            main_sysName = node_info[2]
            node_info[2]=name_map_dict.get(main_sysName,"")
            crtype = node_info[6]
            node_info[6] = CRType_map_info.get(crtype,"")
            test_type = node_info[7]
            node_info[7] = test_type_map_info.get(test_type,"")
            projectstage = node_info[8]
            node_info[8] = ProjectStage_map_info.get(projectstage,"")
            overallschedule = node_info[10]
            node_info[10] = OverallSchedule_map_info.get(overallschedule,"")
            manpowerinput = node_info[12]
            node_info[12] = ManpowerInput_map_info.get(manpowerinput,"")
            versionquality = node_info[13]
            node_info[13] = VersionQuality_map_info.get(versionquality,"")
            workload = node_info[14]
            node_info[14] = Workload_map_info.get(workload,"")
            performancetest = node_info[15]
            node_info[15] = PerformanceTest_map_info.get(performancetest,"")
            if len(node_info) ==16:
                namestr = request.user.last_name+request.user.first_name
                node_info.append(namestr)
            if len(node_info[16]) == 0:
                node_info[16] = request.user.last_name+request.user.first_name
            
            if len(node_info) == 17:#若是缺失后一列的
                datestr = datetime.datetime.now().date().strftime('%Y-%m-%d') 
                node_info.append(datestr)#增加备注信息    
            
            if len(node_info) != 18 :
                continue
            if (len(node_info[5]) == 0) or  ("-" not in node_info[5]):

                node_info[5] = None
            else:
                node_info[5]=datetime.datetime.strptime(node_info[5],"%Y-%m-%d")
                
           
            node_info[17]=datetime.datetime.strptime(node_info[17],"%Y-%m-%d")
            
            try:
                conf_info_tmp = Report_Detail.objects.get(SystemName=node_info[0],
                                                          VersionNum=node_info[1],
                                                          Main_SysName=node_info[2],
                                                          Main_VersionNum=node_info[3])
                
                conf_info_tmp = Report_Detail.objects.filter(SystemName=node_info[0],
                                                          VersionNum=node_info[1],
                                                          Main_SysName=node_info[2],
                                                          Main_VersionNum=node_info[3]).update(ProjectName=node_info[4],
                                                                                               PlanTime=node_info[5],
                                                                                               CRType = node_info[6],
                                                                                               TestType=node_info[7],
                                                                                               ProjectStage=node_info[8],
                                                                                               TestRuns=node_info[9],
                                                                                               OverallSchedule=node_info[10],
                                                                                               Reason=node_info[11],
                                                                                               ManpowerInput=node_info[12],
                                                                                               VersionQuality=node_info[13],
                                                                                               Workload=node_info[14],
                                                                                               PerformanceTest = node_info[15],
                                                                                               Writter=node_info[16],
                                                                                               UpdateDate=node_info[17])
                #conf_info_tmp.save()#更新
            except Report_Detail.DoesNotExist:
                try:
                    
                    conf_info_tmp = Report_Detail(SystemName=node_info[0],
                                                  VersionNum=node_info[1],
                                                  Main_SysName=node_info[2],
                                                  Main_VersionNum=node_info[3],
                                                  ProjectName=node_info[4],
                                                  PlanTime=node_info[5],
                                                  CRType = node_info[6],
                                                  TestType=node_info[7],
                                                  ProjectStage=node_info[8],
                                                  TestRuns=node_info[9],
                                                  OverallSchedule=node_info[10],
                                                  Reason=node_info[11],
                                                  ManpowerInput=node_info[12],
                                                  VersionQuality=node_info[13],
                                                  Workload=node_info[14],
                                                  PerformanceTest = node_info[15],
                                                  Writter=node_info[16],
                                                  UpdateDate=node_info[17])
                    conf_info_tmp.save()#插入
                    
                except:
                    print "\t".join(node_info)
                
        return True       
            
    def read_conf_info_from_db(self):
        '''从数据库中读取Repoer_Detail_Info'''
        conf_info_list = Report_Detail.objects.all()
        sys_source_node_info = {}
        for conf_info in conf_info_list:
            try:
                SystemName=conf_info.SystemName.encode("utf-8")
                VersionNum=conf_info.VersionNum.encode("utf-8")
                Main_SysName=conf_info.Main_SysName.encode("utf-8")
                Main_VersionNum=conf_info.Main_VersionNum.encode("utf-8")
                ProjectName=conf_info.ProjectName.encode("utf-8")
                if conf_info.PlanTime==None:
                    PlanTime = ""
                else:
                    PlanTime=conf_info.PlanTime.strftime('%Y-%m-%d').encode("utf-8")
                
                CRType=conf_info.CRType.encode("utf-8")
                TestType=conf_info.TestType.encode("utf-8")
                ProjectStage=conf_info.ProjectStage.encode("utf-8")
                TestRuns=conf_info.TestRuns.encode("utf-8")
                OverallSchedule=conf_info.OverallSchedule.encode("utf-8")
                Reason=conf_info.Reason.encode("utf-8")
                ManpowerInput=conf_info.ManpowerInput.encode("utf-8")
                VersionQuality=conf_info.VersionQuality.encode("utf-8")
                Workload=conf_info.Workload.encode("utf-8")
                PerformanceTest=conf_info.PerformanceTest.encode("utf-8")
                Writter=conf_info.Writter.encode("utf-8")
                if conf_info.UpdateDate==None:
                    UpdateDate = ""
                else:
                    UpdateDate=conf_info.UpdateDate.strftime('%Y-%m-%d').encode("utf-8")
                    
                    
                if Main_SysName not in sys_source_node_info:
                    sys_source_node_info[Main_SysName] = {}
                if Main_VersionNum not in sys_source_node_info[Main_SysName]:
                    sys_source_node_info[Main_SysName][Main_VersionNum] = []
                sys_source_node_info[Main_SysName][Main_VersionNum].append('''{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}'''.format(SystemName,
                                                                                                                                                                             VersionNum,
                                                                                                                                                                             ProjectName,
                                                                                                                                                                             PlanTime,
                                                                                                                                                                             CRType,
                                                                                                                                                                             TestType,
                                                                                                                                                                             ProjectStage,
                                                                                                                                                                             TestRuns,
                                                                                                                                                                             OverallSchedule,
                                                                                                                                                                             Reason,
                                                                                                                                                                             ManpowerInput,
                                                                                                                                                                             VersionQuality,
                                                                                                                                                                             Workload,
                                                                                                                                                                             PerformanceTest,
                                                                                                                                                                             Writter,
                                                                                                                                                                             UpdateDate))



            except:
                print sys_source_node_info
                       
        return sys_source_node_info



    
'''技术开发部数据交换信息模型'''
class DataExchangeInfo(models.Model):
    service_num=models.CharField(max_length=500, verbose_name = '服务编号')
    service_system=models.CharField(max_length=100, verbose_name = '所属服务体系' )
    main_body=models.CharField(max_length=100, verbose_name = '所属主题域' )
    data_entity=models.CharField(max_length=128, verbose_name = '所属数据实体' )
    data_entity_type=models.CharField(max_length=128, verbose_name = '所属数据实体类型' )
    service_name=models.CharField(max_length=500, verbose_name = '服务名称')
    mep=models.CharField(max_length=50, verbose_name = 'MEP(消息交换模式)' )
    ispublic=models.CharField(max_length=50, verbose_name = '公有/私有' )
    other_interface_num=models.CharField(max_length=50,blank=True, verbose_name = '对方接口编号' )
    interface_name=models.CharField(max_length=500, verbose_name = '接口名称')
    interface_num=models.CharField(max_length=128, verbose_name = '接口编号')
    merge_suggest=models.CharField(max_length=500, verbose_name = '服务合并建议' )
    update_time=models.CharField(max_length=500,blank=True, verbose_name = '服务数据更新时间' )
    update_num=models.CharField(max_length=500, blank=True,verbose_name = '服务数据更新频率' )
    bi_service_number=models.CharField(max_length=500,blank=True, verbose_name = '私有服务同一业务双向交互编号' )
    exchange_method=models.CharField(max_length=500, verbose_name = '数据交换方式' ) 
    publisher=models.CharField(max_length=200, verbose_name = '服务发布者' )
    subscriber=models.CharField(max_length=200, verbose_name = '服务订阅者' )    
    
    
    def save(self, *args, **kwargs):
        '''重写保存方法'''
        super(DataExchangeInfo, self).save(*args, **kwargs) # Call the "real" save() method.
        tmp_info = DataExInfo()#更新sys_info
        tmp_info.refresh_sys_info()
    
    def delete(self, *args, **kwargs):
        #重写删除方法
        super(DataExchangeInfo, self).delete(*args, **kwargs) # Call the "real" delete() method.
        tmp_info = DataExInfo()#更新sys_info
        tmp_info.refresh_sys_info()   
       
    
    def __unicode__(self):
        return '''{0}\t{1}\t{2}\t{3}\t{4}\t{5}\{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}\t{17}'''.format(self.service_num,
                         self.service_system,
                         self.main_body,
                         self.data_entity,
                         self.data_entity_type,
                         self.service_name,
                         self.mep,
                         self.ispublic,
                         self.other_interface_num,
                         self.interface_name,
                         self.interface_num,
                         self.merge_suggest,
                         self.update_time,
                         self.update_num,
                         self.bi_service_number,
                         self.exchange_method,
                         self.publisher,
                         self.subscriber)
        
    class Meta:
        db_table = u"data_exchange"
        verbose_name=u"数据交换信息管理"
        verbose_name_plural=u"数据交换信息管理(总)"



'''系统信息模型 '''     
class SysConfInfo(models.Model):
    node_source=models.CharField(max_length=100, verbose_name = '源系统')
    node_target=models.CharField(max_length=100, verbose_name = '目标系统')
    data_type=models.CharField(max_length=300, verbose_name = '数据类型' )
    conn=models.CharField(max_length=300, verbose_name = '接口' )
    conn_method=models.CharField(max_length=100, verbose_name = '接口方式' )
    type=models.CharField(max_length=100, verbose_name = '类型' )
    def save(self, *args, **kwargs):
        '''重写保存方法'''
        super(SysConfInfo, self).save(*args, **kwargs) # Call the "real" save() method.
        tmp_info = SystemInfo()#更新sys_info
        tmp_info.refresh_sys_info()
    
    def delete(self, *args, **kwargs):
        #重写删除方法
        super(SysConfInfo, self).delete(*args, **kwargs) # Call the "real" delete() method.
        tmp_info = SystemInfo()#更新sys_info
        tmp_info.refresh_sys_info()        
    
    def __unicode__(self):
        return '''{0}\t{1}\t{2}\t{3}\t{4}\t{5}'''.format(self.node_source,
                         self.node_target,
                         self.data_type,
                         self.conn,
                         self.conn_method,
                         self.type)
    class Meta:
        db_table = u"fileupload_sysconfinfo"
        verbose_name=u"系统信息管理"
        verbose_name_plural=u"系统信息管理(总)"


'''手动挖掘信息模型 '''        
class SysDataMineInfo(models.Model):
    node_source=models.CharField(max_length=100, verbose_name='源系统')
    node_target=models.CharField(max_length=100, verbose_name='目标系统')
    data_type=models.CharField(max_length=300, verbose_name='数据类型')
    conn=models.CharField(max_length=300, verbose_name='接口')
    conn_method=models.CharField(max_length=100, verbose_name='接口方式')
    type=models.CharField(max_length=100, verbose_name='类型')
    from_info=models.CharField(max_length=500, verbose_name='挖掘信息来源')

    def __unicode__(self):
        return '''{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'''.format(self.node_source,
                         self.node_target,
                         self.data_type,
                         self.conn,
                         self.conn_method,
                         self.type,
                         self.from_info)
    class Meta:
        db_table = u"fileupload_sysdatamineinfo"
        verbose_name=u"挖掘系统信息管理"
        verbose_name_plural=u"挖掘系统信息管理(总)"            



''' 版本信息模型'''
class VerConfInfo(models.Model):
    IF_CHOICES = (('Y', 'Y'), ('N', 'N'))
    Flow_CHOICES = (('->','->'),('<-','<-'),('<->','<->'))
    Group_CHOICES = (('hx','核心交易平台'),('yh','用户接入平台'),('gg','公共服务平台'),('xx','信息服务平台'),('sj','数据交换平台'),('jyh','交易后处理平台'),('bg','办公支持平台'),('yw','运维平台'),('dsf','第三方托管平台'),('zz','Comstar增值服务平台'))
    main_up_sys_name   =models.CharField(max_length=100, verbose_name = '主升级系统')
    main_up_sys_version=models.CharField(max_length=100, verbose_name = '主升级版本')
    main_up_sys_data_flow=models.CharField(max_length=30,blank=True, choices=Flow_CHOICES, verbose_name = '新增数据流向')
    relevant_sys_group=models.CharField(max_length=100, choices=Group_CHOICES,verbose_name = '关联目标群')
    relevant_sys_name  =models.CharField(max_length=100, verbose_name = '关联系统')
    relevant_sys_version=models.CharField(max_length=100,blank=True, verbose_name = '关联系统版本')
    main_relevant_con_if_test=models.CharField(max_length=10,choices=IF_CHOICES, verbose_name = '是否联测')
    main_relevant_con_if_sync=models.CharField(max_length=10,choices=IF_CHOICES, verbose_name = '是否同步升级')
    depend_detail=models.CharField(max_length=1000,blank=True, verbose_name = '数据依赖备注')
    data_interaction_detail=models.CharField(max_length=1000,blank=True, verbose_name = '数据交互备注')
    remark_col1 = models.CharField(max_length=200,blank=True, verbose_name = '是否已修改')
    remark_col2 = models.CharField(max_length=200,blank=True, verbose_name = '备注2')
    remark_col3 = models.CharField(max_length=200,blank=True, verbose_name = '备注3')
    remark_col4 = models.CharField(max_length=200,blank=True, verbose_name = '备注4')
    def save(self, *args, **kwargs):
        '''重写保存方法'''
        
        '''主升级版本'''
        sys_verinfo = self.main_up_sys_version
        if sys_verinfo.startswith("v"):
            sys_verinfo = "V"+sys_verinfo[1:]
        sys_verinfo = sys_verinfo.replace("。","")
        '''自动补零'''
        sys_verinfo_fields = sys_verinfo.split(".")
        if len(sys_verinfo_fields) == 2:
            sys_verinfo = sys_verinfo+".0.0"
        elif len(sys_verinfo_fields) == 3:
            sys_verinfo = sys_verinfo+".0"
        self.main_up_sys_version = sys_verinfo
         
        '''关联升级版本'''
        sys_verinfo_rel = self.relevant_sys_version
        if sys_verinfo_rel.startswith("v"):
            sys_verinfo_rel = "V"+sys_verinfo_rel[1:]
        sys_verinfo_rel = sys_verinfo_rel.replace("。","")
        '''自动补零'''
        sys_verinfo_rel_fields = sys_verinfo_rel.split(".")
        if len(sys_verinfo_rel_fields) == 2:
            sys_verinfo_rel = sys_verinfo_rel+".0.0"
        elif len(sys_verinfo_rel_fields) == 3:
            sys_verinfo_rel = sys_verinfo_rel+".0"
        self.relevant_sys_version = sys_verinfo_rel
        
        super(VerConfInfo, self).save(*args, **kwargs) # Call the "real" save() method.    
        tmp_info = VersionInfo()#更新ver_info
        tmp_info.refresh_sys_info()
    
    def delete(self, *args, **kwargs):
        #重写删除方法
        super(VerConfInfo, self).delete(*args, **kwargs) # Call the "real" delete() method.    
        tmp_info = VersionInfo()#更新ver_info
        tmp_info.refresh_sys_info() 
    
             
        
    def __unicode__(self):
        return '''{0}\t{1}\t{2}\t{3}'''.format(self.main_up_sys_name,
                         self.main_up_sys_version,
                         self.relevant_sys_name,
                         self.relevant_sys_version)
    class Meta:
        db_table = u"fileupload_verconfinfo"
        verbose_name=u"版本信息管理"
        verbose_name_plural=u"版本信息管理(总)"



@singleton
class DataExInfo(object):
    '''DataEx_info 即为数据交互信息'''
    
    def __init__(self):
        self.sys_info = {}
        self.sys_info = self.read_conf_info_from_db()
    
    def refresh_sys_info(self):
        #更新系统信息
        self.sys_info = self.read_conf_info_from_db()
        return self.sys_info
    
    def update_conf_from_file(self,request,filename="dataex_conf.xlsx"):
        #上传文件后触发,更新文件且插入数据库
        file_path = UPLOAD_FILE_PATH
        in_path = file_path + "/media/pictures/"
        upload_file_path=in_path+filename#上传文件的地址
        user_name = request.user.username
        upload_time = time.strftime('%Y%m%d%H%M', time.localtime())
        csv_path = "{}dataex_conf_{}_{}_{}.csv".format(in_path, filename.split(".")[0], user_name, upload_time)
        csv_path = csv_path.decode("utf-8").encode("gbk")

        if ".xls" in filename:
            #xlsx_path= in_path+filename+".xlsx"#system_conf.xlsx/version.xlsx
            #将上传进来的配置文件改为csv文件,并且改成utf-8的格式
            convert_xlsx_csv(upload_file_path,csv_path)
        elif ".csv" in filename:
            convert_csv_csv(upload_file_path,csv_path)#将gbk修正为utf-8
        self.write_conf_info_to_db(request,csv_path)#插入数据库
        self.refresh_sys_info()#更新sysinfo
        
        
    def write_conf_info_to_db(self,request,file_path):
        '''将信息从文件更新到数据库中'''
        #f_info = open(file_path)
        #sys_info = [val.strip() for val in f_info.readlines()]
        #f_info.close()
        #sys_info = sys_info[1:]
        #sys_info = [val.split("\t") for val in sys_info]

        f_info = open(file_path)
        f_info.readline()  # 舍弃第一行（列名）
        sys_info = (val.strip().split('\t') for val in f_info.readlines())
        f_info.close()
        
        for node_info in sys_info:
            if len(node_info) != 18:
                continue

            try:
                conf_info_tmp = DataExchangeInfo.objects.get(service_num=node_info[0],
                                                        service_system=node_info[1],
                                                        main_body=node_info[2],
                                                        data_entity=node_info[3],
                                                        data_entity_type=node_info[4],
                                                        service_name=node_info[5],
                                                        mep=node_info[6],
                                                        ispublic=node_info[7],
                                                        other_interface_num=node_info[8],
                                                        interface_name=node_info[9],
                                                        interface_num=node_info[10],
                                                        merge_suggest=node_info[11],
                                                        update_time=node_info[12],
                                                        update_num=node_info[13],
                                                        bi_service_number=node_info[14],
                                                        exchange_method=node_info[15],
                                                        publisher=node_info[16],
                                                        subscriber=node_info[17])
                # 若存在，就不更新
                #conf_info_tmp.save()#更新
            except DataExchangeInfo.DoesNotExist:
                try:
                    conf_info_tmp = DataExchangeInfo(service_num=node_info[0],
                                                        service_system=node_info[1],
                                                        main_body=node_info[2],
                                                        data_entity=node_info[3],
                                                        data_entity_type=node_info[4],
                                                        service_name=node_info[5],
                                                        mep=node_info[6],
                                                        ispublic=node_info[7],
                                                        other_interface_num=node_info[8],
                                                        interface_name=node_info[9],
                                                        interface_num=node_info[10],
                                                        merge_suggest=node_info[11],
                                                        update_time=node_info[12],
                                                        update_num=node_info[13],
                                                        bi_service_number=node_info[14],
                                                        exchange_method=node_info[15],
                                                        publisher=node_info[16],
                                                        subscriber=node_info[17])
                    conf_info_tmp.save()#插入
                    
                except:
                    print "\t".join(node_info)
                
        return True       
            
    def read_conf_info_from_db(self):
        '''从数据库中读取dataex_info'''
        conf_info_list = DataExchangeInfo.objects.all()
        sys_source_node_info = {}
        for conf_info in conf_info_list:
            try:
                service_num=conf_info.service_num.encode("utf-8")
                service_system=conf_info.service_system.encode("utf-8")
                main_body=conf_info.main_body.encode("utf-8")
                data_entity=conf_info.data_entity.encode("utf-8")
                data_entity_type=conf_info.data_entity_type.encode("utf-8")
                service_name=conf_info.service_name.encode("utf-8")
                mep=conf_info.mep.encode("utf-8")
                ispublic=conf_info.ispublic.encode("utf-8")
                other_interface_num=conf_info.other_interface_num.encode("utf-8")
                interface_name=conf_info.interface_name.encode("utf-8")
                interface_num=conf_info.interface_num.encode("utf-8")
                merge_suggest=conf_info.merge_suggest.encode("utf-8")
                update_time=conf_info.update_time.encode("utf-8")
                update_num=conf_info.update_num.encode("utf-8")
                bi_service_number=conf_info.bi_service_number.encode("utf-8")
                exchange_method=conf_info.exchange_method.encode("utf-8")
                publisher=conf_info.publisher.encode("utf-8")
                subscriber=conf_info.subscriber.encode("utf-8")

    
                if publisher not in sys_source_node_info:
                    sys_source_node_info[publisher] = {}
                if subscriber not in sys_source_node_info:
                    sys_source_node_info[subscriber] = {}
                #原接口名称    原接口编号    所属数据实体    所属服务名  公有/私有  MEP(消息交换模式) 合并建议   其他修订建议   所属服务体系
                #interface_name,interface_num,data_entity,service_name, ispublic,mep,merge_suggest,other_suggest,service_system
                if subscriber not in sys_source_node_info[publisher]:
                    sys_source_node_info[publisher][subscriber] = []
                if publisher not in sys_source_node_info[subscriber]:
                    sys_source_node_info[subscriber][publisher] = []                    
                
                sys_source_node_info[publisher][subscriber].append('''{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}'''.format(service_num,
                                                                     service_system,
                                                                     main_body,
                                                                     data_entity,
                                                                     data_entity_type,
                                                                     service_name,
                                                                     mep,
                                                                     ispublic,
                                                                     other_interface_num,
                                                                     interface_name,
                                                                     interface_num,
                                                                     merge_suggest,
                                                                     update_time,
                                                                     update_num,
                                                                     bi_service_number,
                                                                     exchange_method))
                mep_reverse = mep.replace("Out","OOO").replace("In","III").replace("OOO","In").replace("III","Out")
                
                sys_source_node_info[subscriber][publisher].append('''{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}'''.format(service_num,
                                                                     service_system,
                                                                     main_body,
                                                                     data_entity,
                                                                     data_entity_type,
                                                                     service_name,
                                                                     mep_reverse,
                                                                     ispublic,
                                                                     other_interface_num,
                                                                     interface_name,
                                                                     interface_num,
                                                                     merge_suggest,
                                                                     update_time,
                                                                     update_num,
                                                                     bi_service_number,
                                                                     exchange_method))                
            except:
                print publisher
                
                
        return sys_source_node_info


@singleton
class SystemInfo(object):
    '''sys_info 即为系统信息'''
    
    def __init__(self):
        self.sys_info = {}
        self.sys_info = self.read_conf_info_from_db()
    
    def refresh_sys_info(self):
        #更新系统信息
        self.sys_info = self.read_conf_info_from_db()
        return self.sys_info
    
    def update_conf_from_file(self,request,filename="system_conf.xlsx"):
        #上传文件后触发,更新文件且插入数据库
        file_path = UPLOAD_FILE_PATH
        in_path = file_path + "/media/pictures/"
        upload_file_path=in_path+filename#上传文件的地址
        user_name = request.user.username
        upload_time = time.strftime('%Y%m%d%H%M', time.localtime())
        csv_path = "{}system_conf_{}_{}_{}.csv".format(in_path, filename.split(".")[0], user_name, upload_time)
        csv_path = csv_path.decode("utf-8").encode("gbk")
        if ".xls" in filename:
            #xlsx_path= in_path+filename+".xlsx"#system_conf.xlsx/version.xlsx
            #将上传进来的配置文件改为csv文件,并且改成utf-8的格式
            convert_xlsx_csv(upload_file_path,csv_path)
        elif ".csv" in filename:
            convert_csv_csv(upload_file_path,csv_path)#将gbk修正为utf-8
        else:
            return
        self.write_conf_info_to_db(request,csv_path)#插入数据库
        self.refresh_sys_info()#更新sysinfo
        
        
    def write_conf_info_to_db(self,request,file_path):
        '''将信息从文件更新到数据库中'''
        f_info = open(file_path)
        f_info.readline()#舍弃第一行（列名）
        sys_info = (val.strip().split('\t') for val in f_info.readlines())
        f_info.close()
        
        for node_info in sys_info:
            if len(node_info) != 6:
                continue
            node_info[0] = convert_name(node_info[0])
            node_info[1] = convert_name(node_info[1])
            try:
                conf_info_tmp = SysConfInfo.objects.get(node_source=node_info[0],
                                                        node_target=node_info[1],
                                                        data_type=node_info[2],
                                                        conn=node_info[3],
                                                        conn_method=node_info[4],
                                                        type=node_info[5])
                '''
                conf_info_tmp.data_type=node_info[2]
                conf_info_tmp.conn=node_info[3]
                conf_info_tmp.conn_method=node_info[4]
                conf_info_tmp.type=node_info[5]
                '''
                #若存在，就不更新
                #conf_info_tmp.save()#更新
            except SysConfInfo.DoesNotExist:
                conf_info_tmp = SysConfInfo(node_source=node_info[0], 
                              node_target=node_info[1],
                              data_type=node_info[2],
                              conn=node_info[3],
                              conn_method=node_info[4],
                              type=node_info[5])
                conf_info_tmp.save()#插入
                
                ct = ContentType.objects.get_for_model(SysConfInfo)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ct.pk,
                    object_id=conf_info_tmp.pk,
                    object_repr=conf_info_tmp.__unicode__(),
                    action_flag=1,
                    change_message="已添加系统信息")
            except SysConfInfo.MultipleObjectsReturned, e:
                '''数据库中存在重复数据？'''
                pass
                
        return True       
            
    def read_conf_info_from_db(self):
        '''从数据库中读取conf_info'''
        conf_info_list = SysConfInfo.objects.all()
        sys_source_node_info = {}
        for conf_info in conf_info_list:
            try:
                node_source=conf_info.node_source.encode("utf-8")
                node_target=conf_info.node_target.encode("utf-8")
                data_type=conf_info.data_type.encode("utf-8")
                conn=conf_info.conn.encode("utf-8")
                conn_method=conf_info.conn_method.encode("utf-8")
                type=conf_info.type.encode("utf-8")
                if node_source not in sys_source_node_info:
                    sys_source_node_info[node_source] = {}
                #数据类型    接口    接口方式    类型
                #data_type,conn,conn_method,type
                if node_target not in sys_source_node_info[node_source]:
                    sys_source_node_info[node_source][node_target] = []
                sys_source_node_info[node_source][node_target].append("{0}\t{1}\t{2}\t{3}\t{4}".format(data_type,
                                                                                     conn,
                                                                                     conn_method,
                                                                                     type,
                                                                                     "该信息来自于系统配置文件"))
            except:
                print node_source
                print node_target
                print data_type
                print conn
                print conn_method
                print type
        return sys_source_node_info
    
@singleton         
class VersionInfo(object):
    '''ver_info 即为版本信息'''
    
    def __init__(self):
        db_info = self.read_conf_info_from_db()
        self.base_info = copy.deepcopy(db_info)
        self.ver_info = copy.deepcopy(db_info)
        self.update_data_without_db()#使得ver_info成为一个闭环
        
    def update_data_without_db(self):
        '''检测所得版本信息中,有无可以更新的地方(闭包)'''
        #self.pass_sync_info()#首先进行一次内部的同步传递挖掘
        need_change_list = []
        for main_up_sys_name in self.ver_info:
            for main_up_sys_version in self.ver_info[main_up_sys_name]:
                for relevant_sys_name in self.ver_info[main_up_sys_name][main_up_sys_version]:
                    for relevant_sys_version in self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name]:
                        if relevant_sys_version == "":#若对应的target系统无版本,则抛弃
                            continue
                        info_list = self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version].split("\t")
                        if info_list[2]=="Y":#若需要补全
                            if (relevant_sys_name == main_up_sys_name) or (relevant_sys_name == "ETL" and main_up_sys_name == "IMIX") or (relevant_sys_name == "IMIX" and main_up_sys_name == "ETL"):
                                continue
                            add_list = [relevant_sys_name,relevant_sys_version,main_up_sys_name,main_up_sys_version,info_list]
                            need_change_list.append(add_list)
        
        for need_change in need_change_list:
            relevant_sys_name,relevant_sys_version,main_up_sys_name,main_up_sys_version,info_list = need_change
            if relevant_sys_name not in self.ver_info:
                self.ver_info[relevant_sys_name] = {}
            if relevant_sys_version not in self.ver_info[relevant_sys_name]:
                self.ver_info[relevant_sys_name][relevant_sys_version] = {}
            if main_up_sys_name not in self.ver_info[relevant_sys_name][relevant_sys_version]:
                self.ver_info[relevant_sys_name][relevant_sys_version][main_up_sys_name] = {}
            if main_up_sys_version not in self.ver_info[relevant_sys_name][relevant_sys_version][main_up_sys_name]:
                if info_list[0] == "->":
                    info_list[0] = "<-"
                elif info_list[0] == "<-":
                    info_list[0] = "->"
                self.ver_info[relevant_sys_name][relevant_sys_version][main_up_sys_name][main_up_sys_version] = "\t".join(info_list)           
                                    
    def pass_sync_info(self):
        '''传递同步升级版本'''
        sync_dict = {}#记录需要同步升级的系统A-B字典关系
        for main_up_sys_name in self.ver_info:
            for main_up_sys_version in self.ver_info[main_up_sys_name]:
                for relevant_sys_name in self.ver_info[main_up_sys_name][main_up_sys_version]:
                    for relevant_sys_version in self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name]:
                        if relevant_sys_version == "":#若对应的target系统无版本,则抛弃
                            continue
                        info_list = self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version].split("\t")
                        if info_list[2]=="Y":#若需要补全
                            if main_up_sys_name+"\t"+main_up_sys_version not in sync_dict:
                                sync_dict[main_up_sys_name+"\t"+main_up_sys_version] = {}
                            sync_dict[main_up_sys_name+"\t"+main_up_sys_version][relevant_sys_name+"\t"+relevant_sys_version] = 1
        need_change_list = []#记录需要修改的系统
        for main_up_sys_name in self.ver_info:
            for main_up_sys_version in self.ver_info[main_up_sys_name]:
                for relevant_sys_name in self.ver_info[main_up_sys_name][main_up_sys_version]:
                    for relevant_sys_version in self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name]:
                        if relevant_sys_version == "":#若对应的target系统无版本,则抛弃
                            continue
                        for val in sync_dict.get(relevant_sys_name+"\t"+relevant_sys_version,[]):#对于B系统对应的所有同步的系统,都进行一次检测
                            c_name,c_version = val.split("\t")
                            if ((c_name == main_up_sys_name) or (c_name == "ETL" and main_up_sys_name == "IMIX") or (c_name == "IMIX" and main_up_sys_name == "ETL")):
                                continue
                            info_list = ["" for val in range(5)]
                            info_list[1]="Y"#传递需要同步更新的值
                            info_list[2]="Y"#传递需要同步更新的值
                            info_list[4]="来自于{0}->{1}系统信息,以及{1}->{2}系统信息".format(main_up_sys_name+main_up_sys_version,relevant_sys_name+relevant_sys_version,c_name+c_version)
                            add_list = [main_up_sys_name,main_up_sys_version,c_name,c_version,info_list]
                            need_change_list.append(add_list)
                            
        for need_change in need_change_list:
            main_up_sys_name,main_up_sys_version,relevant_sys_name,relevant_sys_version,info_list = need_change
    
            if relevant_sys_name not in self.ver_info[main_up_sys_name][main_up_sys_version]:
                self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name] = {}
            if relevant_sys_version not in self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name]:
                self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version] = "\t".join(info_list)
            else:#如果A-C之间已经有了同步关系
                info_list = self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version].split("\t")
                if info_list[2] != "Y":#此处将来可能要标示一下表明该同步信息是来自于同步挖掘
                    info_list[2] = "Y"
                    self.ver_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version] = "\t".join(info_list)
                
                          
        
        for need_change in need_change_list:
            relevant_sys_name,relevant_sys_version,main_up_sys_name,main_up_sys_version,info_list = need_change
            if relevant_sys_name not in self.ver_info:
                self.ver_info[relevant_sys_name] = {}
            if relevant_sys_version not in self.ver_info[relevant_sys_name]:
                self.ver_info[relevant_sys_name][relevant_sys_version] = {}
            if main_up_sys_name not in self.ver_info[relevant_sys_name][relevant_sys_version]:
                self.ver_info[relevant_sys_name][relevant_sys_version][main_up_sys_name] = {}
            if main_up_sys_version not in self.ver_info[relevant_sys_name][relevant_sys_version][main_up_sys_name]:
                if info_list[0] == "->":
                    info_list[0] = "<-"
                elif info_list[0] == "<-":
                    info_list[0] = "->"
                self.ver_info[relevant_sys_name][relevant_sys_version][main_up_sys_name][main_up_sys_version] = "\t".join(info_list)           
    
    def refresh_sys_info(self):
        #更新版本信息
        db_info = self.read_conf_info_from_db()
        self.base_info = copy.deepcopy(db_info)
        self.ver_info = copy.deepcopy(db_info)
        self.update_data_without_db()#使得ver_info成为一个闭环
        return self.ver_info
    
    def change_version(self,sys_verinfo):
        '''主升级版本'''
        try:
            if sys_verinfo.startswith("v"):
                sys_verinfo = "V"+sys_verinfo[1:]
            sys_verinfo = sys_verinfo.replace("。","")
            '''自动补零'''
            sys_verinfo_fields = sys_verinfo.split(".")
            if len(sys_verinfo_fields) == 2:
                sys_verinfo = sys_verinfo+".0.0"
            elif len(sys_verinfo_fields) == 3:
                sys_verinfo = sys_verinfo+".0"    
            return sys_verinfo     
        except:
            return sys_verinfo
            
    def update_conf_from_file(self,request,filename="version_conf.xlsx"):
        #上传文件后触发,更新文件且插入数据库
        file_path = UPLOAD_FILE_PATH
        in_path = file_path + "/media/pictures/"
        upload_file_path = in_path + filename  # 上传文件的地址
        user_name = request.user.username
        upload_time = time.strftime('%Y%m%d%H%M', time.localtime())
        csv_path = "{}version_conf_{}_{}_{}.csv".format(in_path, filename.split(".")[0], user_name, upload_time)
        csv_path = csv_path.decode("utf-8").encode("gbk")

        if ".xls" in filename:
            #xlsx_path= in_path+filename+".xlsx"#system_conf.xlsx/version.xlsx
            #将上传进来的配置文件改为csv文件,并且改成utf-8的格式
            convert_xlsx_csv(upload_file_path,csv_path)
        elif ".csv" in filename:
            convert_csv_csv(upload_file_path,csv_path)#将gbk修正为utf-8
                
        check_list = self.check_if_correct(csv_path)
        if not check_list:
            self.write_conf_info_to_db(request,csv_path)#插入数据库
            self.refresh_sys_info()#更新sysinfo
        return  check_list#若正常,则返回none,否则返回错误的信息
        
    def check_if_correct(self,file_path):
        '''监测当前这个csv文件内容是否正常,有无冲突行'''
        conflict_list = []

        f_info = open(file_path)
        f_info.readline()  # 舍弃第一行（列名）
        ver_info = (val.strip().split('\t') for val in f_info.readlines())
        f_info.close()
        
        for index,node_info in enumerate(ver_info):
            if len(node_info) == 8:#若是缺失后两列的
                node_info.append("")
                node_info.append("")#增加备注信息
            elif len(node_info) == 9:#若是缺失后一列的
                node_info.append("")#增加备注信息    
            elif len(node_info) != 10:#若列数不达10个
                continue
            node_info[1] = self.change_version(node_info[1])
            node_info[5] = self.change_version(node_info[5])    
            #名字归一
            node_info[0] = convert_name(node_info[0])
            node_info[4] = convert_name(node_info[4])                       
            try:
                #[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version]
                if node_info[5] == "":#如果版本号为空,则不进入下面的监测而跳过
                    continue
                conf_info_tmp = VerConfInfo.objects.get(main_up_sys_name=node_info[4],
                                                        main_up_sys_version=node_info[5],
                                                        relevant_sys_name=node_info[0],
                                                        relevant_sys_version=node_info[1])
                if_old_bidirection = (conf_info_tmp.main_up_sys_data_flow == "<->")
                if_new_bidirection = (node_info[2] == "<->")
                if not ((if_old_bidirection and if_new_bidirection) or (conf_info_tmp.main_up_sys_data_flow != node_info[2])):
                    '''上传的数据流向与之前的不能吻合 第X行的X数据与之前X有冲突'''
                    
                    conflict_list.append("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(index+2,\
                                          "-".join([node_info[0],node_info[1],node_info[2],node_info[4],node_info[5]]),\
                                          "-".join([conf_info_tmp.main_up_sys_name,\
                                           conf_info_tmp.main_up_sys_version,\
                                           conf_info_tmp.main_up_sys_data_flow,\
                                           conf_info_tmp.relevant_sys_name,\
                                           conf_info_tmp.relevant_sys_version]))) 

            except VerConfInfo.DoesNotExist:
                pass
        if len(conflict_list) > 0:
            return conflict_list#返回冲突数据
        return None#返回空值
        
    def write_conf_info_to_db(self,request,file_path):
        '''将信息从文件更新到数据库中'''
        #f_info = open(file_path)
        #ver_info = [val.strip() for val in f_info.readlines()]
        #f_info.close()
        #ver_info = ver_info[1:]
        #ver_info = [val.split("\t") for val in ver_info]

        f_info = open(file_path)
        f_info.readline()  # 舍弃第一行（列名）
        ver_info = (val.strip().split('\t') for val in f_info.readlines())
        f_info.close()
        
        for node_info in ver_info:
            if len(node_info) == 8:#若是缺失后两列的
                node_info.append("")
                node_info.append("")#增加备注信息
            elif len(node_info) == 9:#若是缺失后一列的
                node_info.append("")#增加备注信息
            elif len(node_info) != 10:#若列数不达10个
                continue
            

            node_info[1] = self.change_version(node_info[1])
            node_info[5] = self.change_version(node_info[5])
            #名字归一
            node_info[0] = convert_name(node_info[0])
            node_info[4] = convert_name(node_info[4])            
            try:
                #[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version]
                conf_info_tmp = VerConfInfo.objects.get(main_up_sys_name=node_info[0],
                                            main_up_sys_version=node_info[1],
                                            relevant_sys_name=node_info[4],
                                            relevant_sys_version=node_info[5])
                conf_info_tmp.main_up_sys_data_flow=node_info[2]
                conf_info_tmp.relevant_sys_group=node_info[3]
                conf_info_tmp.main_relevant_con_if_test=node_info[6]
                conf_info_tmp.main_relevant_con_if_sync=node_info[7]
                conf_info_tmp.depend_detail=node_info[8]
                conf_info_tmp.data_interaction_detail=node_info[9]

                #若存在，就不更新
                #conf_info_tmp.save()#更新
            except VerConfInfo.DoesNotExist:
                conf_info_tmp = VerConfInfo(main_up_sys_name=node_info[0], 
                              main_up_sys_version=node_info[1],
                              main_up_sys_data_flow=node_info[2],
                              relevant_sys_group=node_info[3],
                              relevant_sys_name=node_info[4],
                              relevant_sys_version=node_info[5],
                              main_relevant_con_if_test=node_info[6],
                              main_relevant_con_if_sync=node_info[7],
                              depend_detail=node_info[8],
                              data_interaction_detail=node_info[9]
                              )
                conf_info_tmp.save()#插入
                
                ct = ContentType.objects.get_for_model(VerConfInfo)
                LogEntry.objects.log_action(
                    user_id=request.user.id, 
                    content_type_id=ct.pk,
                    object_id=conf_info_tmp.pk,
                    object_repr=conf_info_tmp.__unicode__(),
                    action_flag=1,
                    change_message="已添加版本信息")
                             
        return True       
            
    def  read_conf_info_from_db(self):
        '''从数据库中读取conf_info'''
        conf_info_list = VerConfInfo.objects.all()
        ver_source_node_info = {}
        for conf_info in conf_info_list:
            main_up_sys_name   =conf_info.main_up_sys_name.encode("utf-8")
            main_up_sys_version=conf_info.main_up_sys_version.encode("utf-8")
            main_up_sys_data_flow=conf_info.main_up_sys_data_flow.encode("utf-8")
            relevant_sys_group=conf_info.relevant_sys_group.encode("utf-8")
            relevant_sys_name  =conf_info.relevant_sys_name.encode("utf-8")
            relevant_sys_version=conf_info.relevant_sys_version.encode("utf-8")
            main_relevant_con_if_test=conf_info.main_relevant_con_if_test.encode("utf-8")
            main_relevant_con_if_sync=conf_info.main_relevant_con_if_sync.encode("utf-8")
            depend_detail=conf_info.depend_detail.encode("utf-8")
            data_interaction_detail=conf_info.data_interaction_detail.encode("utf-8")
            #主升级系统    升级版本    本版本新增数据的流向    关联系统项目群    关联系统    关联版本    关联系统是否联测    关联系统是否升级    详情    继续详情
            #main_up_sys_name    main_up_sys_version    main_up_sys_data_flow    ……
            if main_up_sys_name not in ver_source_node_info:
                ver_source_node_info[main_up_sys_name] = {}
            if main_up_sys_version not in ver_source_node_info[main_up_sys_name]:
                ver_source_node_info[main_up_sys_name][main_up_sys_version] = {}
            if relevant_sys_name not in ver_source_node_info[main_up_sys_name][main_up_sys_version]:
                ver_source_node_info[main_up_sys_name][main_up_sys_version][relevant_sys_name] = {}
            if relevant_sys_version not in ver_source_node_info[main_up_sys_name][main_up_sys_version][relevant_sys_name]:
                ver_source_node_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version] = {}
            #main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail
            ver_source_node_info[main_up_sys_name][main_up_sys_version][relevant_sys_name][relevant_sys_version] = "{}\t{}\t{}\t{}\t{}".format(main_up_sys_data_flow,
                                                                                     main_relevant_con_if_test,
                                                                                     main_relevant_con_if_sync,
                                                                                     depend_detail,
                                                                                     data_interaction_detail)
        return ver_source_node_info
    
        
class Picture(models.Model):
    """This is a small demo using just two fields. The slug field is really not
    necessary, but makes the code simpler. ImageField depends on PIL or
    pillow (where Pillow is easily installable in a virtualenv. If you have
    problems installing pillow, use a more generic FileField instead.

    """
    file = models.ImageField(upload_to="pictures")
    slug = models.SlugField(max_length=50, blank=True)

    def __unicode__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(Picture, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(Picture, self).delete(*args, **kwargs)
