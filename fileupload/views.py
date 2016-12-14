# encoding: utf-8
import csv
import os
from django.views.generic import CreateView, DeleteView, ListView
from .models import Picture
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from django.db import connection,transaction
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import Context
from .models import *
from fileupload.login_form import LoginForm,ChangepwdForm
from django.shortcuts import render_to_response,render,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from bootstrap_toolkit.widgets import BootstrapUneditableInput
from get_legend_info import Legend_Info_System,DataEX_Legend_Info_System
from django.http import JsonResponse,StreamingHttpResponse
from data_mine import sycn_sys_ver_info
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from cm_vrms_upload.settings import UPLOAD_FILE_PATH


'''读取系统配置信息'''
all_sys_types = ["system_conf","version_conf"]
key_node = ["外汇交易系统","本币交易系统","X-Swap"]
data_type_list = ["交易数据","基础数据","交易后数据","曲线数据","行情数据","统计数据"]
data_method_list = ["ETL","IMIX","MQ","FTP(SFTP)","DBLink"]#注FTP(SFTP)可能在数据中是分开的,需要将这两个合并
UN_NEED_SYCN = ["ETL","IMIX中间件","IMIX"]#无需同步的系统列表
system_info = SystemInfo()
version_info = VersionInfo()
dataex_info = DataExInfo()
SysName_info = SysNameInfo()
testreport_info = Report_DetailInfo()
sys_query_result = SysConfInfo.objects.all()
base_version_info = version_info.read_conf_info_from_db()#未做闭环时的version_info

sycn_sys_ver_info(system_info,base_version_info)#初始化时协同


def hello(request):

    return HttpResponse("Hello world")

def test_form(request):
    return render_to_response('test_form.html')

def show_form(request):
    if 'q' in request.GET:
        message = 'You searched for: %r' % request.GET['q']
    else:
        message = 'You submitted an empty form.'
    return HttpResponse(message)
def system_detail(request):
    '''系统详情'''
    s_info = system_info.sys_info
    source_node_list = s_info.keys()
    c = Context({'STATIC_URL': '/static/'})
    c["node_list_1"] = [val for val in source_node_list if val in key_node]
    c["node_list_2"] = [val for val in source_node_list if val not in key_node]
    c["jump_to"] = "system_node_detail"#指示接下来跳转的位置
    out_path = "system_detail"
    out_title = "外汇交易中心在建系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    return render_to_response(out_path+'.html',context_instance=c)
def system_detail_mine(request):
    system_info.refresh_sys_info()#首先更新数据库
    base_version_info = version_info.read_conf_info_from_db()#未做闭环时的version_info
    sycn_sys_ver_info(system_info,base_version_info)#初始化时协同
    return system_detail(request)

def system_search_detail(request):
    '''系统详情'''
    s_info = system_info.sys_info
    request_node_name = request.GET["query"].encode("utf-8")
    source_node_list = [val for val in s_info if request_node_name.lower() in val.lower()]
    for val in source_node_list:
        val = val.encode("utf-8")
    if(len(source_node_list)) == 0:#若没有查到,则返回全量页面
        return system_detail(request)
    c = Context({'STATIC_URL': '/static/'})
    c["node_list_1"] = [val for val in source_node_list if val in key_node]
    c["node_list_2"] = [val for val in source_node_list if val not in key_node]
    c["jump_to"] = "system_node_detail"#指示接下来跳转的位置
    out_path = "system_detail"
    out_title = "外汇交易中心在建系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    return render_to_response(out_path+'.html',context_instance=c)

def version_detail(request):
    '''版本详情'''
    v_info = version_info.ver_info
    source_node_name_list = v_info.keys()
    c = Context({'STATIC_URL': '/static/'})
    c["node_list_1"] = [val for val in source_node_name_list if val in key_node]
    c["node_list_2"] = [val for val in source_node_name_list if val not in key_node]
    c["jump_to"] = "version_detail_for_one_system"#version_node_detail指示接下来跳转的位置
    out_path = "version_detail"
    #out_title = "版本"
    c["out_title"] = "外汇交易中心在建系统"#指示接下来跳转的位置
    c["search_type"] = "versys_search_detail"
    return render_to_response(out_path+'.html',context_instance=c)

def versys_search_detail(request):
    '''版本中系统详情'''
    request_node_name = request.GET["query"].encode("utf-8")
    v_info = version_info.ver_info
    source_node_list = [val for val in v_info if request_node_name.lower() in val.lower()]
    for val in source_node_list:
        val = val.encode("utf-8")
    if(len(source_node_list)) == 0:#若没有查到,则返回全量页面
        #return system_detail(request)
        return version_detail(request)
    c = Context({'STATIC_URL': '/static/'})
    c["node_list_1"] = [val for val in source_node_list if val in key_node]
    c["node_list_2"] = [val for val in source_node_list if val not in key_node]
    c["jump_to"] = "version_detail_for_one_system"#指示接下来跳转的位置
    out_path = "version_detail"
    out_title = "系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    c["search_type"] = "versys_search_detail"#查找方式
    return render_to_response(out_path+'.html',context_instance=c)

def versys2_search_detail(request):
    '''版本中更进一步的版本号详情'''
    request_node_name = request.GET["query_node"].encode("utf-8")
    request_node_version = request.GET["query"].encode("utf-8")

    v_info = version_info.ver_info
    if request_node_name not in v_info :
        if request_node_name in system_info.sys_info:
            return HttpResponseRedirect('/system_node_detail_'+request_node_name+'/')#重定向到该系统的关联图
        else:
            return HttpResponseRedirect('/version_detail/')#重定向到版本页之初

    version_lists = v_info[request_node_name]
    node_version_list = [request_node_name+"\t"+val for val in version_lists if request_node_version.lower() in val.lower()]#组合成"系统名+版本号"的形式
    c = Context({'STATIC_URL': '/static/'})
    if request_node_name in key_node:
        c["node_list_1"] = node_version_list
    else:
        c["node_list_2"] = node_version_list
    c["jump_to"] = "version_node_detail"#指示接下来跳转的位置
    out_path = "version_detail"
    out_title = request_node_name#"版本"
    c["out_title"] = out_title#指示接下来跳转的位置
    c["node_name"] = request_node_name
    c["search_type"] = "versys2_search_detail"#查找方式
    return render_to_response(out_path+'.html',context_instance=c)

def version_detail_for_one_system(request):#将一个系统的所有版本列出来,这个是气泡版本
    v_info = version_info.ver_info
    request_node_name = request.path[:-1].replace("/version_detail_for_one_system_","").encode("utf-8")
    if request_node_name not in v_info :
        if request_node_name in system_info.sys_info:
            return HttpResponseRedirect('/system_node_detail_'+request_node_name+'/')#重定向到该系统的关联图
        else:
            return HttpResponseRedirect('/version_detail/')#重定向到版本页之初

    version_lists = v_info[request_node_name]
    node_version_list = [request_node_name+"\t"+val for val in version_lists]#组合成"系统名+版本号"的形式
    c = Context({'STATIC_URL': '/static/'})
    if request_node_name in key_node:
        c["node_list_1"] = node_version_list
    else:
        c["node_list_2"] = node_version_list
    c["jump_to"] = "version_node_net"#指示接下来跳转的位置
    out_path = "version_detail"
    out_title = request_node_name#"版本"
    c["out_title"] = out_title#指示接下来跳转的位置
    c["node_name"] = request_node_name
    c["search_type"] = "versys2_search_detail"#查找方式
    return render_to_response(out_path+'.html',context_instance=c)


def system_node_detail(request):
    '''显示sys节点的内容system_node_detail'''
    s_info = system_info.sys_info
    request_node_name = request.path[:-1].replace("/system_node_detail_","").encode("utf-8")

    node_info = {}
    if request_node_name in s_info:
        for target in s_info[request_node_name]:
            node_info[target] = s_info[request_node_name][target][::]
    else:
        request.path = "/system_detail/"
        return system_detail(request)
    for node in node_info:
        node_info[node] = "|||".join(node_info[node])
    c = Context({'STATIC_URL': '/static/'})
    c["source_info"] = request_node_name
    node_list = node_info.keys()
    c["target_list"] = node_list
    c["source_target_info"] = node_info
    out_title = "系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    '''legend信息'''
    legend_info = Legend_Info_System(s_info[request_node_name])
    full_legend,full_category,legend_node_info = legend_info.get_legend_list()
    c["legend_list"] = full_legend
    '''categories信息'''
    c["category_list"] =  full_category
    '''更详细的node信息'''
    #构造所有的node信息,方便category_index查找
    c["node_category_list"] =  legend_node_info

    return render_to_response('sys_node_detail.html',context_instance=c)

def version_node_detail(request):
    '''显示version节点的内容version_node_detail'''
    v_info = version_info.ver_info
    request_node_name_version = request.path[:-1].replace("/version_node_detail_","").encode("utf-8")
    if "|" not in request_node_name_version:
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #request_node_name = request_node_name_version.split("|")[0]
    #request_node_version = request_node_name_version.split("|")[1]
    request_node_name, request_node_version = request_node_name_version.split('|')
    if "V" not in request_node_version:
        return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    node_info = {}
    if request_node_name in v_info:
        if request_node_version in v_info[request_node_name]:
            node_info = v_info[request_node_name][request_node_version]
        else:
            return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    else:
        #request.path = "/version_detail/"
        #return version_detail(request)
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #数据流,关联系统是否联测  ,关联系统是否升级 ,depend_detail,data_interaction_detail
    c = Context({'STATIC_URL': '/static/'})
    source_node = request_node_name+"\t"+request_node_version
    c["source_info"] = source_node#源点
    node_list = []
    target_node_info = {}
    for node_name in node_info:
        for version in node_info[node_name]:
            target_node = node_name+"\t"+version
            node_list.append(node_name+"\t"+version)#目标节点
            target_node_info[target_node] = node_info[node_name][version]
    c["target_list"] = node_list#所有的目标系统
    c["source_target_info"] = target_node_info
    c["target_need_sync"] = [node_name_version for node_name_version in node_list if target_node_info[node_name_version].split("\t")[2]=="Y"]
    c["target_need_test"] = [node_name_version for node_name_version in node_list if target_node_info[node_name_version].split("\t")[1]=="Y" and node_name_version not in c["target_need_sync"]]
    c["target_others"] = [node_name_version for node_name_version in node_list if node_name_version not in c["target_need_test"] and node_name_version not in c["target_need_sync"]]
    out_title = "版本"
    c["out_title"] = out_title#指示接下来跳转的位置
    #c["source_download_info"] = request_node_name+"|"+request_node_version
    c["source_download_info"] = request_node_name_version
    return render_to_response('version_node_detail.html',context_instance=c)


def convert_info_table(source_target_node_info):#'{{source_info}} - {{taget}}':'{{s_t_info}}',
    #将关联信息,转化为table格式展示
    result = "<table border='1'>"
    result += "<tr><th>源系统</th><th>目标系统</th><th>新增数据流向</th><th>数据交互备注</th></tr>"
    for node_info in source_target_node_info:
        source,target = node_info.split(" - ")
        s_t_info = source_target_node_info[node_info].split("\t")
        s_t_info[3] = s_t_info[3].strip()
        if len(s_t_info[3]) < 1:
            continue
        result += "<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>".format(source,target,s_t_info[0],s_t_info[3])
    result += "</table>"
    return result


def version_node_net_old(request):
    '''显示网状图'''
    #v_info = version_info.base_info#未做闭环时的version_info
    v_info = version_info.ver_info
    request_node_name_version = request.path[:-1].replace("/version_node_net_","").encode("utf-8")
    if "|" not in request_node_name_version:
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    request_node_name = request_node_name_version.split("|")[0]
    request_node_version = request_node_name_version.split("|")[1]
    if "V" not in request_node_version:
        return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    node_info = {}
    if request_node_name in v_info:
        if request_node_version in v_info[request_node_name]:
            node_info = v_info[request_node_name][request_node_version]
        else:
            return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    else:
        #request.path = "/version_detail/"
        #return version_detail(request)
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #数据流,关联系统是否联测  ,关联系统是否升级 ,depend_detail,data_interaction_detail
    c = Context({'STATIC_URL': '/static/'})
    source_node = request_node_name+"\t"+request_node_version

    target_source_info = {}#目标系统-源系统-[info_list]
    for node_name in node_info:
        for version in node_info[node_name]:
            target_node = node_name+"\t"+version
            if target_node not in target_source_info:
                target_source_info[target_node] = {}
            target_source_info[target_node][source_node] = node_info[node_name][version]#将两者之间的关系信息保存下来
            if len(version) > 0 and (node_name in v_info) and (version in v_info[node_name]):#若需要扩展(满足有外拓系统的条件下)
                #第二轮扩展开始
                second_node_info = v_info[node_name][version]
                for second_node_name in second_node_info:
                    for second_version in second_node_info[second_node_name]:
                        second_target_node = second_node_name+"\t"+second_version
                        if second_target_node not in target_source_info:
                            target_source_info[second_target_node] = {}
                        target_source_info[second_target_node][target_node] = second_node_info[second_node_name][second_version]
    #划分node到每种类型
    sync_node_list = []
    test_node_list = []
    others_list = []
    all_node_list = [sync_node_list,test_node_list,others_list]
    for taget_node in target_source_info:
        add_list = []
        for tmp_source_node in target_source_info[taget_node]:
            put_type = 2#默认其他
            priority = 1#默认为二级关系
            need_sync = (target_source_info[taget_node][tmp_source_node].split("\t")[2]=="Y")
            need_test = (target_source_info[taget_node][tmp_source_node].split("\t")[1]=="Y")
            if need_sync:
                put_type = 0
            elif need_test:
                put_type = 1
            else:
                put_type = 2
            if tmp_source_node == source_node:
                priority = 0
            else:
                priority = 1
            add_list.append([put_type,priority])
        first_relation = [val[0] for val in add_list if val[1] == 0]#与源节点相连
        if len(first_relation) > 0:
            all_node_list[first_relation[0]].append(taget_node)
        else:
            all_node_list[min([val[0] for val in add_list])].append(taget_node)#存放到优先级最高(put_type最小)的list

    pair_list = []#{source : '{{source_info}}', target : '{{ target }}', weight : 6},
    edge_filter = set()#记录那些边能有,如果已经出现过,就不要再添加进去
    source_target_node_info = {}#'{{source_info}} - {{taget}}':'{{s_t_info}}',
    for taget_node in target_source_info:
        for tmp_source_node in target_source_info[taget_node]:
            if taget_node+" - "+tmp_source_node in edge_filter:#如果该边已经出现了,就不要再加入
                continue
            edge_filter.add(tmp_source_node+" - "+taget_node)
            edge_filter.add(taget_node+" - "+tmp_source_node)
            source_target_node_info[tmp_source_node+" - "+taget_node] = target_source_info[taget_node][tmp_source_node]#存放弹框的信息
            weight = 1
            need_sync = (target_source_info[taget_node][tmp_source_node].split("\t")[2]=="Y")
            need_test = (target_source_info[taget_node][tmp_source_node].split("\t")[1]=="Y")
            if need_sync:
                weight = '6'
            elif need_test:
                weight = '4'
            else:
                weight = '1'

            data_flow = target_source_info[taget_node][tmp_source_node].split("\t")[0]
            if data_flow == "->":
                tmp_out_str = "{source : '"+tmp_source_node+"', target : '"+taget_node+"', weight : "+weight+"},"
                pair_list.append(tmp_out_str)
            elif data_flow == "<-":
                tmp_out_str = "{source : '"+taget_node+"', target : '"+tmp_source_node+"', weight : "+weight+"},"
                pair_list.append(tmp_out_str)
            elif data_flow =="<->":
                tmp_out_str1 = "{source : '"+tmp_source_node+"', target : '"+taget_node+"', weight : "+weight+"},"
                pair_list.append(tmp_out_str1)
                tmp_out_str2 = "{source : '"+taget_node+"', target : '"+tmp_source_node+"', weight : "+weight+"},"
                pair_list.append(tmp_out_str2)
            else:
                tmp_out_str = "{source : '"+tmp_source_node+"', target : '"+taget_node+"', weight : "+weight+"},"
                pair_list.append(tmp_out_str)

    c["source_info"] = source_node#源点
    c["target_need_sync"] = all_node_list[0]
    c["target_need_test"] = all_node_list[1]
    c["target_others"] = all_node_list[2]
    c["pair_list"] = pair_list
    out_title = "版本"
    c["out_title"] = out_title#指示接下来跳转的位置
    c["source_target_info"] = source_target_node_info
    c["table_content"] = convert_info_table(source_target_node_info)
    c["source_download_info"] = request_node_name+"|"+request_node_version
    return render_to_response('version_node_net.html',context_instance=c)

def get_update_time_table_info(all_need_list):
    cursor = connection.cursor()
    return_str = ""
    for need_node_info in all_need_list:
        sysname,version = need_node_info.split("\t")
        if len(version) == 0:
            continue
        need_sql = "select AppName,AppVersion,UpdateDate,environment_fir from update_time where AppName='"+sysname+"' and AppVersion='"+version+"';"
        cursor.execute(need_sql)
        count_currentnum = cursor.fetchall()
        uat_time = ""
        moni_time = ""
        for val in count_currentnum:
            AppName,AppVersion,UpdateDate,environment_fir = val
            if u"模拟环境" in environment_fir:
                moni_time = UpdateDate
            else:
                uat_time = UpdateDate
        out_list = [sysname,version,uat_time,moni_time]
        format_str =  "<tr>"+"<td>{}</td>"*len(out_list)+"</tr>"
        out_str = format_str.format(*out_list)
        #该项目版本历次升级信息的详情展示
        return_str += out_str.encode("utf-8")
    cursor.close()
    return return_str


def version_node_net(request):
    '''显示网状图'''
    #v_info = version_info.base_info#未做闭环时的version_info
    v_info = version_info.ver_info
    request_node_name_version = request.path[:-1].replace("/version_node_net_","").encode("utf-8")
    if "|" not in request_node_name_version:
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #request_node_name = request_node_name_version.split("|")[0]
    #request_node_version = request_node_name_version.split("|")[1]
    request_node_name, request_node_version = request_node_name_version.split('|')
    if "V" not in request_node_version:
        return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    node_info = {}
    if request_node_name in v_info:
        if request_node_version in v_info[request_node_name]:
            node_info = v_info[request_node_name][request_node_version]
        else:
            return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    else:
        #request.path = "/version_detail/"
        #return version_detail(request)
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #数据流,关联系统是否联测  ,关联系统是否升级 ,depend_detail,data_interaction_detail
    c = Context({'STATIC_URL': '/static/'})
    source_node = request_node_name+"\t"+request_node_version

    target_source_info = {}#目标系统-源系统-[info_list]
    for node_name in node_info:
        for version in node_info[node_name]:
            target_node = node_name+"\t"+version
            if target_node not in target_source_info:
                target_source_info[target_node] = {}
            target_source_info[target_node][source_node] = node_info[node_name][version]#将两者之间的关系信息保存下来

    #划分node到每种类型
    sync_node_list = []
    test_node_list = []
    others_list = []
    all_node_list = [sync_node_list,test_node_list,others_list]
    for taget_node in target_source_info:
        add_list = []
        for tmp_source_node in target_source_info[taget_node]:
            put_type = 2#默认其他
            priority = 1#默认为二级关系
            need_sync = (target_source_info[taget_node][tmp_source_node].split("\t")[2]=="Y")
            need_test = (target_source_info[taget_node][tmp_source_node].split("\t")[1]=="Y")

            if need_sync:
                put_type = 0
            elif need_test:
                put_type = 1
            else:
                put_type = 2
            if tmp_source_node == source_node:
                priority = 0
            else:
                priority = 1
            add_list.append([put_type,priority])
        first_relation = [val[0] for val in add_list if val[1] == 0]#与源节点相连
        if len(first_relation) > 0:
            all_node_list[first_relation[0]].append(taget_node)
        else:
            all_node_list[min([val[0] for val in add_list])].append(taget_node)#存放到优先级最高(put_type最小)的list

    pair_list = []#{source : '{{source_info}}', target : '{{ target }}', weight : 6},
    edge_filter = set()#记录那些边能有,如果已经出现过,就不要再添加进去
    source_target_node_info = {}#'{{source_info}} - {{taget}}':'{{s_t_info}}',
    comm_node = {}#存放  传输节点(ETL、IMIX):与主节点关系(联测、同步)
    comm_i = {}#存放每种 没有版本号的传输介质,目前已经放了多少个了,如{ETL:0} 且将node修正为  " "*i+"ETL" + " "*i的格式
    for taget_node in target_source_info:
        for tmp_source_node in target_source_info[taget_node]:
            if taget_node+" - "+tmp_source_node in edge_filter:#如果该边已经出现了,就不要再加入
                continue
            #格式形如 ETL V (同步)、IMIX V (联测)
            tmp_comm_node_str = target_source_info[taget_node][tmp_source_node].split("\t")[3]
            tmp_comm_node_str = tmp_comm_node_str.replace("（","(").replace("）",")")
            tmp_comm_node_list = tmp_comm_node_str.split("、")
            for tmp_node_relation_str in tmp_comm_node_list:
                tmp_node_relation = tmp_node_relation_str.split("(")
                tmp_comm_node = ""
                tmp_comm_relation = ""#与主节点的关系
                if len(tmp_node_relation) == 2:
                    tmp_comm_node,tmp_comm_relation = tmp_node_relation
                else:
                    tmp_comm_node = "".join(tmp_node_relation_str.split())
                    tmp_comm_relation = ""
                if "v" in tmp_comm_node.lower() and "." in tmp_comm_node.lower():
                    #如果是有版本号的传输node
                    if len(comm_node.get(tmp_comm_node,"").strip()) == 0:
                        comm_node[tmp_comm_node] = tmp_comm_relation
                else:
                    comm_i[tmp_comm_node] = comm_i.get(tmp_comm_node,-1) + 1#至少开始从0开始计数
                    #形成  n个空格  + ETL + n个空格  的形式
                    tmp_comm_node = comm_i[tmp_comm_node] * " " + tmp_comm_node + comm_i[tmp_comm_node] * " "
                    if len(comm_node.get(tmp_comm_node,"").strip()) == 0:
                        comm_node[tmp_comm_node] = tmp_comm_relation

                #下面的操作 对备注的每一个传输依赖node都需要进行
                edge_filter.add(tmp_source_node+" - "+taget_node)
                edge_filter.add(taget_node+" - "+tmp_source_node)
                append_str = "\t{}\t{}".format("".join(tmp_source_node.split()),"".join(taget_node.split()))
                source_target_node_info[tmp_source_node+" - "+tmp_comm_node] = target_source_info[taget_node][tmp_source_node]+append_str#存放弹框的信息
                source_target_node_info[tmp_comm_node+" - "+taget_node] = target_source_info[taget_node][tmp_source_node]+append_str#存放弹框的信息
                weight = 1
                need_sync = (target_source_info[taget_node][tmp_source_node].split("\t")[2]=="Y")
                need_test = (target_source_info[taget_node][tmp_source_node].split("\t")[1]=="Y")
                if need_sync:
                    weight = '6'
                elif need_test:
                    weight = '4'
                else:
                    weight = '2'
                    comm_node[tmp_comm_node] = "其他"#此处的node表明，自己本身不是同步or联测，且关联的节点也不是同步or联测

                data_flow = target_source_info[taget_node][tmp_source_node].split("\t")[0]

                if data_flow == "->":
                    tmp_out_str = "{source : '"+tmp_source_node+"', target : '"+tmp_comm_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str)
                    tmp_out_str = "{source : '"+tmp_comm_node+"', target : '"+taget_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str)
                elif data_flow == "<-":
                    tmp_out_str = "{source : '"+taget_node+"', target : '"+tmp_comm_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str)
                    tmp_out_str = "{source : '"+tmp_comm_node+"', target : '"+tmp_source_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str)
                elif data_flow =="<->":
                    tmp_out_str1 = "{source : '"+tmp_source_node+"', target : '"+tmp_comm_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str1)
                    tmp_out_str1 = "{source : '"+tmp_comm_node+"', target : '"+taget_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str1)
                    tmp_out_str2 = "{source : '"+taget_node+"', target : '"+tmp_comm_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str2)
                    tmp_out_str2 = "{source : '"+tmp_comm_node+"', target : '"+tmp_source_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str2)
                else:
                    tmp_out_str = "{source : '"+tmp_source_node+"', target : '"+tmp_comm_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str)
                    tmp_out_str = "{source : '"+tmp_comm_node+"', target : '"+taget_node+"', weight : "+weight+"},"
                    pair_list.append(tmp_out_str)

    c["source_info"] = source_node#源点
    c["target_need_sync"] = all_node_list[0]
    c["target_need_test"] = all_node_list[1]
    c["target_others"] = all_node_list[2]
    #comm_node = {}#存放  传输节点(ETL、IMIX):与主节点关系(联测、同步)
    c["comm_node_others"] = [val for val in comm_node if "联测" not in comm_node[val] and "同步" not in comm_node[val] and "其他" not in comm_node[val]]#该部分继续显示"传输介质"
    c["comm_node_others_true"] = [val for val in comm_node if "其他" in comm_node[val]]
    c["comm_node_need_test"] = [val for val in comm_node if "联测" in comm_node[val]]
    c["comm_node_need_sync"] = [val for val in comm_node if "同步" in comm_node[val]]

    c["pair_list"] = pair_list#连线
    out_title = "版本"
    c["out_title"] = out_title#指示接下来跳转的位置
    c["source_target_info"] = source_target_node_info
    c["table_content"] = convert_info_table(source_target_node_info)
    #c["source_download_info"] = request_node_name+"|"+request_node_version
    c["source_download_info"] = request_node_name_version

    all_need_list = [source_node] + sum(all_node_list,[])
    c["out_str"] = get_update_time_table_info(all_need_list)

    return render_to_response('version_node_net.html',context_instance=c)


def version_node_detail_csv(request):#输出csv文件
    '''显示version节点的内容version_node_detail'''
    v_info = version_info.ver_info
    request_node_name_version = request.path[:-1].replace("/version_node_csv_detail_","").encode("utf-8")
    if "|" not in request_node_name_version:
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #request_node_name = request_node_name_version.split("|")[0]
    #request_node_version = request_node_name_version.split("|")[1]
    request_node_name, request_node_version = request_node_name_version.split('|')
    if "V" not in request_node_version:
        return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    node_info = {}
    if request_node_name in v_info:
        if request_node_version in v_info[request_node_name]:
            node_info = v_info[request_node_name][request_node_version]
        else:
            return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    else:
        #request.path = "/version_detail/"
        #return version_detail(request)
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初

    response = HttpResponse(content_type='text/csv')
    # force download.
    out_name = request_node_name_version.replace("|","")
    response['Content-Disposition'] = 'attachment;filename='+out_name+'版本详情.csv'
    writer = csv.writer(response)
    writer.writerow([u'主升级系统'.encode("gbk"),u'主升级版本'.encode("gbk"),u'新增数据流向'.encode("gbk"),u'关联目标群'.encode("gbk"),u'关联系统'.encode("gbk"),u'关联系统版本'.encode("gbk"),u'是否联测'.encode("gbk"),u'是否同步升级'.encode("gbk"),u'数据依赖备注'.encode("gbk"),u'数据交互备注'.encode("gbk")])
    #main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail
    request_node_name_w = request_node_name.decode("utf-8").encode("gbk")
    request_node_version_w = request_node_version.decode("utf-8").encode("gbk")
    for node_name in node_info:
        node_name_w = node_name.decode("utf-8").encode("gbk")
        for version in node_info[node_name]:
            version_w = version.decode("utf-8").encode("gbk")
            tmp_info = node_info[node_name][version].decode("utf-8").encode("gbk")
            main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail =tmp_info.split("\t")
            writer.writerow([request_node_name_w,request_node_version_w,main_up_sys_data_flow,"",node_name_w,version_w,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail])
    return response

def version_net_detail_csv(request):#输出csv文件
    '''显示version节点的网状内容version_node_detail'''
    #v_info = version_info.base_info
    v_info = version_info.ver_info
    request_node_name_version = request.path[:-1].replace("/version_net_detail_csv_","").encode("utf-8")
    if "|" not in request_node_name_version:
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #request_node_name = request_node_name_version.split("|")[0]
    #request_node_version = request_node_name_version.split("|")[1]
    request_node_name, request_node_version = request_node_name_version.split('|')
    if "V" not in request_node_version:
        return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    node_info = {}
    if request_node_name in v_info:
        if request_node_version in v_info[request_node_name]:
            node_info = v_info[request_node_name][request_node_version]
        else:
            return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    else:
        #request.path = "/version_detail/"
        #return version_detail(request)
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初

    response = HttpResponse(content_type='text/csv')
    # force download.
    out_name = request_node_name_version.replace("|","")
    source_node = request_node_name+"\t"+request_node_version
    target_source_info = {}#目标系统-源系统-[info_list]
    for node_name in node_info:
        for version in node_info[node_name]:
            target_node = node_name+"\t"+version
            if target_node not in target_source_info:
                target_source_info[target_node] = {}
            target_source_info[target_node][source_node] = node_info[node_name][version]#将两者之间的关系信息保存下来

    edge_filter = set()#记录那些边能有,如果已经出现过,就不要再添加进去
    source_target_node_info = {}#'{{source_info}} - {{taget}}':'{{s_t_info}}',
    for taget_node in target_source_info:
        for tmp_source_node in target_source_info[taget_node]:
            #if taget_node+" - "+tmp_source_node in edge_filter:#如果该边已经出现了,就不要再加入,但在输出数据详情的时候,还是要记入
                #continue
            #edge_filter.add(tmp_source_node+" - "+taget_node)
            edge_filter.add(taget_node+" - "+tmp_source_node)
            source_target_node_info[tmp_source_node+" - "+taget_node] = target_source_info[taget_node][tmp_source_node]#存放弹框的信息

    response['Content-Disposition'] = 'attachment;filename='+out_name+'网状版本详情.csv'
    writer = csv.writer(response)
    writer.writerow([u'主升级系统'.encode("gbk"),u'主升级版本'.encode("gbk"),u'新增数据流向'.encode("gbk"),u'关联目标群'.encode("gbk"),u'关联系统'.encode("gbk"),u'关联系统版本'.encode("gbk"),u'是否联测'.encode("gbk"),u'是否同步升级'.encode("gbk"),u'数据依赖备注'.encode("gbk"),u'数据交互备注'.encode("gbk")])
    #main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail
    for source_target_node_name_version in source_target_node_info:
        source,target = source_target_node_name_version.split(" - ")
        source_node_name,source_node_version = source.split("\t")
        source_node_name_w = source_node_name.decode("utf-8").encode("gbk")
        source_node_version_w = source_node_version.decode("utf-8").encode("gbk")
        target_node_name,target_node_version = target.split("\t")
        target_node_name_w = target_node_name.decode("utf-8").encode("gbk")
        target_node_version_w = target_node_version.decode("utf-8").encode("gbk")
        tmp_info = source_target_node_info[source_target_node_name_version].decode("utf-8").encode("gbk")
        main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail =tmp_info.split("\t")
        writer.writerow([source_node_name_w,source_node_version_w,main_up_sys_data_flow,"",target_node_name_w,target_node_version_w,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail])
    return response


def version_net_detail_csv_old(request):#输出csv文件
    '''显示version节点的网状内容version_node_detail'''
    #v_info = version_info.base_info
    v_info = version_info.ver_info
    request_node_name_version = request.path[:-1].replace("/version_net_detail_csv_","").encode("utf-8")
    if "|" not in request_node_name_version:
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初
    #request_node_name = request_node_name_version.split("|")[0]
    #request_node_version = request_node_name_version.split("|")[1]
    request_node_name, request_node_version = request_node_name_version.split('|')
    if "V" not in request_node_version:
        return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    node_info = {}
    if request_node_name in v_info:
        if request_node_version in v_info[request_node_name]:
            node_info = v_info[request_node_name][request_node_version]
        else:
            return HttpResponseRedirect('/version_detail_for_one_system_'+request_node_name+'/')#重定向到某个系统具体版本页之初
    else:
        #request.path = "/version_detail/"
        #return version_detail(request)
        return HttpResponseRedirect('/version_detail/')#重定向到版本页之初

    response = HttpResponse(content_type='text/csv')
    # force download.
    out_name = request_node_name_version.replace("|","")
    source_node = request_node_name+"\t"+request_node_version
    target_source_info = {}#目标系统-源系统-[info_list]
    for node_name in node_info:
        for version in node_info[node_name]:
            target_node = node_name+"\t"+version
            if target_node not in target_source_info:
                target_source_info[target_node] = {}
            target_source_info[target_node][source_node] = node_info[node_name][version]#将两者之间的关系信息保存下来
            if len(version) > 0 and (node_name in v_info) and (version in v_info[node_name]):#若需要扩展(满足有外拓系统的条件下)
                #第二轮扩展开始
                second_node_info = v_info[node_name][version]
                for second_node_name in second_node_info:
                    for second_version in second_node_info[second_node_name]:
                        second_target_node = second_node_name+"\t"+second_version
                        if second_target_node not in target_source_info:
                            target_source_info[second_target_node] = {}
                        target_source_info[second_target_node][target_node] = second_node_info[second_node_name][second_version]

    edge_filter = set()#记录那些边能有,如果已经出现过,就不要再添加进去
    source_target_node_info = {}#'{{source_info}} - {{taget}}':'{{s_t_info}}',
    for taget_node in target_source_info:
        for tmp_source_node in target_source_info[taget_node]:
            #if taget_node+" - "+tmp_source_node in edge_filter:#如果该边已经出现了,就不要再加入,但在输出数据详情的时候,还是要记入
                #continue
            #edge_filter.add(tmp_source_node+" - "+taget_node)
            edge_filter.add(taget_node+" - "+tmp_source_node)
            source_target_node_info[tmp_source_node+" - "+taget_node] = target_source_info[taget_node][tmp_source_node]#存放弹框的信息

    response['Content-Disposition'] = 'attachment;filename='+out_name+'网状版本详情.csv'
    writer = csv.writer(response)
    writer.writerow([u'主升级系统'.encode("gbk"),u'主升级版本'.encode("gbk"),u'新增数据流向'.encode("gbk"),u'关联目标群'.encode("gbk"),u'关联系统'.encode("gbk"),u'关联系统版本'.encode("gbk"),u'是否联测'.encode("gbk"),u'是否同步升级'.encode("gbk"),u'数据依赖备注'.encode("gbk"),u'数据交互备注'.encode("gbk")])
    #main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail
    for source_target_node_name_version in source_target_node_info:
        source,target = source_target_node_name_version.split(" - ")
        source_node_name,source_node_version = source.split("\t")
        source_node_name_w = source_node_name.decode("utf-8").encode("gbk")
        source_node_version_w = source_node_version.decode("utf-8").encode("gbk")
        target_node_name,target_node_version = target.split("\t")
        target_node_name_w = target_node_name.decode("utf-8").encode("gbk")
        target_node_version_w = target_node_version.decode("utf-8").encode("gbk")
        tmp_info = source_target_node_info[source_target_node_name_version].decode("utf-8").encode("gbk")
        main_up_sys_data_flow,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail =tmp_info.split("\t")
        writer.writerow([source_node_name_w,source_node_version_w,main_up_sys_data_flow,"",target_node_name_w,target_node_version_w,main_relevant_con_if_test,main_relevant_con_if_sync,depend_detail,data_interaction_detail])
    return response

@login_required(login_url='/login/')
def upload_file(request):
    if request.method == "POST":
        upload_state = False#文件上传成功标志
        try:
            upload_state = handle_uploaded_file(request.FILES['t_file'])
        except:
            c = Context({'STATIC_URL': '/static/'})
            c["message"] = "请上传文件"
            c["alert_cont"] = "upload_file_system"
            return render_to_response('alert_and_jump.html',context_instance=c)

        if upload_state:
            file_conf = request.FILES['t_file'].name
            #file_conf = file_conf.replace(".xlsx","")
            if "system" in request.path:#若更新系统文件
                system_info.update_conf_from_file(request,filename=file_conf)#file_conf = system_conf
                #return system_detail(request)#输出系统页面

                return HttpResponseRedirect('/system_detail/')#重定向
            elif "version" in request.path:
                check_list = version_info.update_conf_from_file(request,filename=file_conf)#file_conf = version_conf
                if check_list:#若有出错的行,则输出
                    c = Context({'STATIC_URL': '/static/'})
                    c["if_check_list"] = True
                    c["check_list"] = check_list
                    return render_to_response('upload_form.html',context_instance=c)
                else:
                    #return version_detail(request)#输出系统页面
                    return HttpResponseRedirect('/version_detail/')#重定向
            elif "dataex" in request.path:
                check_list = dataex_info.update_conf_from_file(request,filename=file_conf)#file_conf = version_conf
                if check_list:#若有出错的行,则输出
                    c = Context({'STATIC_URL': '/static/'})
                    c["if_check_list"] = True
                    c["check_list"] = check_list
                    return render_to_response('upload_form.html',context_instance=c)
                else:
                    #return version_detail(request)#输出系统页面
                    return HttpResponseRedirect('/dataex_detail/')#重定向
            elif "Sysname" in request.path:
                check_list = SysName_info.update_conf_from_file(request,filename=file_conf)#file_conf = version_conf
                if check_list:#若有出错的行,则输出（不可能有错，函数没有返回值，始终返回None）
                    c = Context({'STATIC_URL': '/static/'})
                    c["if_check_list"] = True
                    c["check_list"] = check_list
                    return render_to_response('upload_form.html',context_instance=c)
                else:
                    #return version_detail(request)#输出系统页面
                    return HttpResponseRedirect('/test_report_index/')#重定向

            elif "testreport" in request.path:
                check_list = testreport_info.update_conf_from_file(request,filename=file_conf)#file_conf = version_conf
                if check_list:#若有出错的行,则输出
                    c = Context({'STATIC_URL': '/static/'})
                    c["if_check_list"] = True
                    c["check_list"] = check_list
                    return render_to_response('upload_form.html',context_instance=c)
                else:
                    #return version_detail(request)#输出系统页面
                    return HttpResponseRedirect('/test_report_index/')#重定向

    c = RequestContext(request)
    c['STATIC_URL'] = '/static/'
    return render_to_response('upload_form.html',context_instance=c)


def handle_uploaded_file(f):#将文件上传到指定位置
    file_path = UPLOAD_FILE_PATH + "/media/pictures"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    f_path = file_path+"/"+f.name

    with open(f_path, 'wb+') as info:
        for chunk in f.chunks():
            info.write(chunk)
    return True


"""dataex的相关操作"""
def dataex_detail(request):
    '''dataex的详情'''
    s_info = dataex_info.sys_info
    source_node_list = s_info.keys()
    c = Context({'STATIC_URL': '/static/'})
    c["node_list_1"] = [val for val in source_node_list if val in key_node]
    c["node_list_2"] = [val for val in source_node_list if val not in key_node]
    c["jump_to"] = "dataex_node_detail"#指示接下来跳转的位置
    out_path = "show_dataex"
    out_title = "外汇交易中心在建系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    return render_to_response(out_path+'.html',context_instance=c)

def dataex_search_detail(request):
    '''交互搜索详情'''
    s_info = dataex_info.sys_info
    request_node_name = request.GET["query"].encode("utf-8")
    source_node_list = [val for val in s_info if request_node_name.lower() in val.lower()]
    for val in source_node_list:
        val = val.encode("utf-8")
    if(len(source_node_list)) == 0:#若没有查到,则返回全量页面
        return dataex_detail(request)
    c = Context({'STATIC_URL': '/static/'})
    c["node_list_1"] = [val for val in source_node_list if val in key_node]
    c["node_list_2"] = [val for val in source_node_list if val not in key_node]
    c["jump_to"] = "dataex_node_detail"#指示接下来跳转的位置
    out_path = "show_dataex"
    out_title = "外汇交易中心在建系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    return render_to_response(out_path+'.html',context_instance=c)

def dataex_node_detail(request):
    '''显示dataex节点的内容dataex_node_detail'''
    s_info = dataex_info.sys_info
    request_node_name = request.path[:-1].replace("/dataex_node_detail_","").encode("utf-8")

    node_info = {}
    if request_node_name in s_info:
        for target in s_info[request_node_name]:
            node_info[target] = s_info[request_node_name][target][::]
    else:
        request.path = "/show_dataex/"
        return dataex_detail(request)
    for node in node_info:
        node_info[node] = "|||".join(node_info[node])
    c = Context({'STATIC_URL': '/static/'})
    c["source_info"] = request_node_name
    node_list = node_info.keys()
    c["target_list"] = node_list
    c["source_target_info"] = node_info
    out_title = "系统"
    c["out_title"] = out_title#指示接下来跳转的位置
    '''legend信息'''
    legend_info = DataEX_Legend_Info_System(s_info[request_node_name])
    full_legend,full_category,legend_node_info = legend_info.get_legend_list()
    c["legend_list"] = full_legend
    '''categories信息'''
    c["category_list"] = full_category
    '''更详细的node信息'''
    #构造所有的node信息,方便category_index查找
    c["node_category_list"] = legend_node_info

    return render_to_response('dataex_node_detail.html',context_instance=c)



def login(request):
    '''用户登录'''
    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('login.html', RequestContext(request, {'form': form,}))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(request.GET['next'])
            else:
                return render_to_response('login.html', RequestContext(request, {'form': form,'password_is_wrong':True}))
        else:
            return render_to_response('login.html', RequestContext(request, {'form': form,}))

#@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/upload_file/")

@login_required
def changepwd(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render_to_response('changepwd.html', RequestContext(request, {'form': form,}))
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = auth.authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return HttpResponseRedirect('/upload_file/')
            else:
                return render_to_response('changepwd.html', RequestContext(request, {'form': form, 'oldpassword_is_wrong': True}))
        else:
            return render_to_response('changepwd.html', RequestContext(request, {'form': form}))


class PictureCreateView(CreateView):
    model = Picture

    def form_valid(self, form):
        self.object = form.save()
        files = [serialize(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class BasicVersionCreateView(PictureCreateView):
    template_name_suffix = '_basic_form'


class BasicPlusVersionCreateView(PictureCreateView):
    template_name_suffix = '_basicplus_form'


class AngularVersionCreateView(PictureCreateView):
    template_name_suffix = '_angular_form'


class jQueryVersionCreateView(PictureCreateView):
    template_name_suffix = '_jquery_form'


class PictureDeleteView(DeleteView):
    model = Picture

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class PictureListView(ListView):
    model = Picture

    def render_to_response(self, context, **response_kwargs):
        files = [ serialize(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
