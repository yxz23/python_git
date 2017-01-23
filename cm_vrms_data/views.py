#-*-coding:utf-8-*-
import os

from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.template import RequestContext, Context
from django.views.decorators.csrf import csrf_exempt

import data_handler


def data_index(request):
    c = {}
    upload_state = False
    cur_user = request.user
    if request.method == "POST":
        if request.FILES.has_key('u_file'):
            show_name = request.POST['show_name']
            upload_state = data_handler.upload_file(request.FILES['u_file'], show_name, cur_user.username)
            c['show_item'] = show_name  # 上传成功后显示该表格
        else:
            print 'have not chosen a file.'

    c['logined'] = cur_user.is_authenticated()  # 用户登录状态
    c['upload_perm'] = cur_user.has_perm('cm_vrms_data.table_upload') if cur_user.is_authenticated() else False#上传权限
    c['left_html_data'] = data_handler.get_left_data()
    return render_to_response('data_index.html', RequestContext(request, c))


def get_json_data(request, data_info):
    '''通过ajax来获取json数据'''
    data_json = {}
    table_data, page_data = data_handler.get_right_data(data_info)#获取右侧页面所需数据
    data_json['table'] = table_data
    data_json['page'] = page_data
    return JsonResponse(data_json)


def download_file(request, file_name):
    '''下载文件'''
    file_path = data_handler.find_file(file_name)
    if file_path == '':
        print 'can not find the resource file!'
        return HttpResponseRedirect('/data_index/')

    response = HttpResponse(data_handler.read_file_block(file_path), content_type = 'APPLICATION/OCTET-STREAM')
    response['Content-Disposition'] = 'attachment; filename={}.{}'.format(file_name, file_path.split('.')[-1])
    response['Content-Length'] = os.path.getsize(file_path)
    return response


'''------------上下分属不同页面------------'''


def script_index(request):
    c = {}
    c['menu_os'], c['menu_database'] = data_handler.get_menu_list()
    c['trows'] = data_handler.get_trow_list()
    return render_to_response('script_index.html', context_instance= RequestContext(request, c))


def get_json_script(request, filter_info):
    '''根据过滤条件更新脚本列表html'''
    filter_list = filter_info.split('/')
    if filter_list[0] == u'全部操作系统':
        filter_list[0] = ''
    elif filter_list[0] == u'无':
        filter_list[0] = None
    if filter_list[1] == u'全部数据库':
        filter_list[1] = ''
    elif filter_list[1] == u'无':
        filter_list[1] = None
    tab_json = {}
    #tab_json['tbody'] = data_handler.get_trows_html(os_type=filter_list[0], app_name=filter_list[1])
    tab_json['tbody'] = data_handler.get_trow_list(os_type=filter_list[0], app_name=filter_list[1])
    return JsonResponse(tab_json)


@csrf_exempt
def script_download(request):

    zip_path = data_handler.add_zip(request.POST.getlist('script_action'))

    response = HttpResponse(data_handler.read_file_block(zip_path), content_type = 'APPLICATION/OCTET-STREAM')
    response['Content-Disposition'] = 'attachment; filename={}'.format(zip_path.split('/')[-1])
    response['Content-Length'] = os.path.getsize(zip_path)
    return response
