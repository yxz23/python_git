from django.shortcuts import render
# encoding: utf-8
import os
from django.http import HttpResponse,HttpResponseRedirect  
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import Context
from django.shortcuts import render_to_response,render,get_object_or_404  
from django.contrib.auth.models import User  
from django.contrib import auth
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from bootstrap_toolkit.widgets import BootstrapUneditableInput 
from django.http import JsonResponse


from django.db.models import Avg, Max, Min, Count
from django.shortcuts import render_to_response
import MySQLdb
import datetime
import re
import time
from  cm_vrms_wiki.models import CM_Application,Appserver
from .models import Envi_Detail,Envi_Relation
from django.db import connection,transaction


ETL_node ="ETL"
IMIX_node = "IMIX"

# Create your views here.
def update_table_from_wiki(request):
    '''由Appserver表'''
    '''AppServerID,ChineseName,remark,serviceip,port,service_name'''
    #appserver_info_list = Appserver.objects.all().order_by('AppID_id','ServiceIP')#appserver所有信息
    appserver_info_list = Appserver.objects.filter(AppID_id__isnull = False).exclude(Remark__exact = '')
    #Envi_Detail.objects.all().delete()
 
    need_data_dict = {}
    for appserver_info in appserver_info_list:
        AppID_Raw = appserver_info.AppID
        #if (AppID_Raw is None):
        #    continue
        AppID = AppID_Raw.AppID
        ChineseName = AppID_Raw.ChineseName.encode("utf-8")
        ServiceIP=appserver_info.ServiceIP
        Usage = appserver_info.Usage.encode("utf-8")
        Remark = appserver_info.Remark.encode("utf-8")
        #if (Remark==''):
        #    continue
        one_need_data_list = [AppID,ChineseName,Remark]
        one_need_data_list = [str(val) for val in one_need_data_list]
        one_need_data_key = "_\t_".join(one_need_data_list)
        if(one_need_data_key) not in need_data_dict:
            need_data_dict[one_need_data_key] = []
        need_data_dict[one_need_data_key].append(ServiceIP+" "+Usage)
    
    
    insert_db_list = []
    for app_info in need_data_dict:
        AppID,ChineseName,Remark = app_info.split("_\t_")
        ip_info = "|".join(need_data_dict[app_info])
        tmp_db_list = [AppID,ChineseName,Remark,ip_info]
        insert_db_list.append(tmp_db_list)
    for one_db_list in insert_db_list:
        AppID,ChineseName,Remark,ip_info = one_db_list
        AppID = int(AppID)
        print "\t".join(one_db_list)
        try :
            envi_info_tmp = Envi_Detail.objects.get(AppID=AppID, 
                                         AppName=ChineseName,
                                         EnviName=Remark,
                                         IP_Usage=ip_info)
        except Envi_Detail.DoesNotExist:
            
            envi_info_tmp = Envi_Detail(AppID=AppID, 
                          AppName=ChineseName,
                          EnviName=Remark,
                          IP_Usage=ip_info)
            envi_info_tmp.save()#插入          
  
    return HttpResponseRedirect('/show_middleware/')#重定向

def show_middleware(request):
    '''系统环境导览页'''
    s_info = Envi_Relation.objects.all()
    need_show_list = []
    for s_node_info in s_info:
        one_node_ID = s_node_info.AppID_Source
        one_node_name = one_node_ID.AppName
        one_node_envi = one_node_ID.EnviName
        one_node_info = " | ".join([one_node_name, one_node_envi])
        if one_node_info not in need_show_list:
            need_show_list.append(one_node_info)
    
    c = Context({'STATIC_URL': '/static/'})
    
    c["need_show_list_ETL"] = [val for val in need_show_list if ETL_node in val]
    c["need_show_list_IMIX"] = [val for val in need_show_list if IMIX_node in val]
    c["jump_to"] = "middleware_detail"#指示接下来跳转的位置
    out_path = "show_middleware"
    out_title = "系统环境"
    c["out_title"] = out_title#页面标题
    return render_to_response(out_path+'.html',context_instance=c)


def middleware_search(request):
    if 'query' in request.GET:
        request_node_name = request.GET["query"]
    s_info = Envi_Relation.objects.all()
    need_show_list = []
    for s_node_info in s_info:
        one_node = s_node_info.AppID_Source
        one_node_info = " | ".join([one_node.AppName, one_node.EnviName])
        if (one_node_info in need_show_list) or (request_node_name.lower() not in one_node_info.lower()):
            continue
        need_show_list.append(one_node_info)

    c = Context({'STATIC_URL': '/static/'})

    c["need_show_list_ETL"] = [val for val in need_show_list if ETL_node in val]
    c["need_show_list_IMIX"] = [val for val in need_show_list if IMIX_node in val]
    c["jump_to"] = "middleware_detail"  # 指示接下来跳转的位置
    out_title = "系统环境"
    return render_to_response('show_middleware.html', context_instance = c)


#将数据库中存在的服务器类型信息的转化成对应的中文名
convert_dict = {
                "application":"应用",
                "db":"数据库",
                "app&db":"应用&数据库",
                }

def replace_word(normal_str):
    for key in convert_dict:
        normal_str = normal_str.replace(key,convert_dict[key])
    return normal_str


def get_state_dict(info_dict):
    res_dict = {}#返回字典{'name' : True}
    ip_dict = {}#利用该字典求交集{'name' : set(ip)}

    if len(info_dict) == 1:
        '''如果长度为1，无须求交集，状态设置为False，直接返回'''
        for key in info_dict:
            res_dict[key] = False
        return res_dict

    rc = re.compile(r'(?:\d{1,3}\.?){4}')
    for key in info_dict:
        ip_str = info_dict[key]
        ip_dict[key] = set(rc.findall(ip_str))#获取ip集合

        '''初始状态设置为False'''
        res_dict[key] = False

    '''遍历求ip交集，如果交集不为空，设置状态为True'''
    for key in info_dict:
        s_ip = ip_dict.pop(key)
        for k_ip in ip_dict:
            set_info = s_ip & ip_dict[k_ip]
            if len(set_info) > 0:
                res_dict[key] = True
                res_dict[k_ip] = True
    return res_dict

def middleware_detail(request):
    '''系统环境详情'''
    request_node_name_envi = request.path[:-1].replace("/middleware_detail_", "")
    source_AppName, source_EnviName = request_node_name_envi.split(" | ")
    s_info = Envi_Relation.objects.filter(AppID_Source__AppName = source_AppName).filter(AppID_Source__EnviName = source_EnviName)
    relation_pair_dict={}
    source_info_dict={}
    target_info_dict={}
    
    node_info_dict={}#将源节点和目标节点的IP及服务器类型信息都放在一个字典中
    
    for one_node_info in s_info:
        source_Id = one_node_info.AppID_Source
        target_Id = one_node_info.AppID_Target
        source_name = source_Id.AppName
        source_Envi = source_Id.EnviName
        source_IPinfo = source_Id.IP_Usage
        source_IPinfo = replace_word(source_IPinfo)
        target_name = target_Id.AppName
        target_Envi = target_Id.EnviName
        target_IPinfo = target_Id.IP_Usage
        target_IPinfo = replace_word(target_IPinfo)
        one_relation_source=[source_name,source_Envi]
        one_relation_target = [target_name,target_Envi]
        one_relation_target = " | ".join(one_relation_target)
        one_relation_key = " | ".join(one_relation_source)
        if (one_relation_key) not in relation_pair_dict:
            relation_pair_dict[one_relation_key]=[]
        relation_pair_dict[one_relation_key].append(one_relation_target)
        
        if (one_relation_key) not in source_info_dict:
            source_info_dict[one_relation_key]=source_IPinfo
            
        if (one_relation_target) not in target_info_dict:
            target_info_dict[one_relation_target]=target_IPinfo
            
        
    node_info_dict=dict(source_info_dict.items()+target_info_dict.items())

    #获取是否存在相同IP
    state_dict = get_state_dict(node_info_dict)

    #补充ip信息
    if request_node_name_envi in node_info_dict:
        request_node_name_ip = node_info_dict[request_node_name_envi]
    else:
        request.path = "/show_middleware/"
        return show_middleware(request)        
    

    if request_node_name_envi in relation_pair_dict:
        target_info = relation_pair_dict[request_node_name_envi]
    else:
        request.path = "/show_middleware/"
        return show_middleware(request)
    
    c = Context({'STATIC_URL': '/static/'})
 
    out_title = "系统"

    target_info_list = []
    for val in target_info:
        if val in node_info_dict:
            target_info_list.append({'info':"name:'{}',ip:'{}'".format(val, node_info_dict[val]), 'state': state_dict[val]})

    c["request_node_name_envi"] = {'name' : request_node_name_envi, 'state' : state_dict[request_node_name_envi]}
    c["request_node_name_ip"] = request_node_name_ip
    c["target_list"] = target_info
    c["target_info_list"] = target_info_list
    c["out_title"] = out_title#页面标题
    return render_to_response('middleware_detail.html',context_instance=c)
