#-*-coding:utf-8-*-
import os
import datetime
from math import ceil
import zipfile

from fileupload.models import convert_xlsx_csv, convert_csv_csv
from test_report.get_page_list import get_page_list
from .models import Upload_Table

from xml_parse import Conf_Xml_Data

_file_path = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/') + '/media/files'
_export_path = _file_path + '/export/'
_page_step = 10  # 每页显示数据条目数

_script_path = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/') + '/media/scripts/'


def save_to_sql(show_name, user_name):
    '''将上传文件信息添加至数据库'''
    try:
        '''若存在，更新上传时间'''
        data_record = Upload_Table.objects.get(ShowName=show_name)
        data_record.UploadTime = datetime.datetime.now()
        data_record.save()
    except Upload_Table.DoesNotExist:
        '''若不存在，则插入数据'''
        data_info = Upload_Table(ShowName=show_name, UserName=user_name)
        data_info.save()


def upload_file(f, show_name, user_name):#将文件上传到指定位置
    if not os.path.exists(_file_path):
        os.makedirs(_file_path)
    f_path = _file_path+"/"+f.name

    with open(f_path, 'wb+') as info:
        for chunk in f.chunks():
            info.write(chunk)

    csv_path = "{}/{}.csv".format(_file_path, show_name)
    csv_path = csv_path.decode("utf-8").encode("gbk")
    if ".xls" in f.name:
        # 将上传进来的配置文件改为csv文件,并且改成utf-8的格式
        convert_xlsx_csv(f_path, csv_path)
    elif ".csv" in f.name:
        convert_csv_csv(f_path, csv_path)  # 将gbk修正为utf-8

    '''上传源文件移至导出文件夹'''
    xls_file = ''.join([_export_path, show_name, '.xls'])
    xlsx_file = ''.join([_export_path, show_name, '.xlsx'])
    if os.path.exists(xls_file):
        os.remove(xls_file)
        os.rename(f_path, xls_file)
    elif os.path.exists(xlsx_file):
        os.remove(xlsx_file)
        os.rename(f_path, xlsx_file)
    else:
        os.rename(f_path, ''.join([_export_path, show_name, '.', f_path.split('.')[-1]]))

    '''上传信息更新至数据库'''
    save_to_sql(show_name, user_name)
    return True


def get_left_html():
    html_dict = {'sys': ''}
    for info in Upload_Table.objects.all():
        html_dict['sys'] = ''.join(
            [html_dict['sys'],
             '<a href="#" class="list-group-item" id="sys_',
             info.ShowName,
             '_1" data-toggle="tooltip" data-placement="top" title="',
             info.UserName,
             '" onclick="update(id)">',
             info.ShowName, '</a>'])
    return html_dict


def get_table_html(data_info):
    '''data_info 格式：sys_fileName_currentPage'''
    info_list = data_info.encode('utf-8').replace('/', '').split('_')
    table_name = '_'.join(info_list[1 : -1]).strip('_')#获取表名
    current_page = int(info_list[-1])#获取当前页码
    file_name = ''.join([_file_path, '/', table_name, '.csv']).decode('utf-8')
    table_html = '<div style="margin-top:15px"><div style="text-align:center;font-size:large;font-weight:bolder">{0}</div>'\
                 '<div class="btn-group" style="float:right;margin:-20px 80px 20px 0">'\
                 '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">'\
                 '<span class="glyphicon glyphicon-share-alt"></span>&nbsp;&nbsp;导出<span class="caret"></span>'\
                 '</button><ul class="dropdown-menu" role="menu"><li><a href="/data_download/{0}">'\
                 '<span class="glyphicon glyphicon-circle-arrow-down"></span>&nbsp;导出Excel</a></li></ul></div></div>' \
                 '<table class="table table-condensed table-hover table-bordered"><thead><tr>'.format(table_name)
    with open(file_name) as f_info:
        head_info = f_info.readline()  # 表头信息
        head_info = head_info.strip().split('\t')
        for item in head_info:
            table_html = ''.join([table_html, '<th>', item, '</th>'])
        table_html += '</tr></thead><tbody>'
        body_info = [val.strip().split('\t') for val in f_info.readlines()]
        for row_info in body_info[(current_page - 1) * _page_step : current_page * _page_step]:
            '''只截取需要显示的数据行'''
            table_html += '<tr>'
            for item in row_info:
                table_html = ''.join([table_html, '<td>', item, '</td>'])
            table_html += '</tr>'
        table_html += '</tbody></table>'
    page_html = get_page_html(len(body_info), data_info)#根据总记录数和当前页信息获取页码html
    return table_html, page_html


def get_page_html(record_count, data_info):
    '''获取页码列表，并为页码添加超链接'''
    info_list = data_info.encode('utf-8').replace('/', '').split('_')
    current_page = int(info_list[-1])
    file_url = '_'.join(info_list[:-1])
    page_list = get_page_list(current_page, int(ceil(record_count / float(_page_step))))
    page_html = '<ul class="pagination">'
    for page in page_list:
        if page in [str(current_page), '...']:
            '''当前页和省略号无需加超链接'''
            page_html += ''.join(['<li class="disabled"><a>', page, '</a></li>'])
        else:
            page_html += ''.join(['<li><a href="#"', 'onclick="update(\'', file_url, '_', page, '\')">', page, '</a></li>'])
    return page_html


def find_file(file_name, path_type='export'):
    if path_type == 'export':
        xls_file = ''.join([_export_path, file_name, '.xls'])
        xlsx_file = ''.join([_export_path, file_name, '.xlsx'])
    else:
        xls_file = ''.join([_file_path, '/', file_name, '.csv'])
        xlsx_file = ''
    if os.path.exists(xls_file):
        return xls_file
    elif os.path.exists(xlsx_file):
        return xlsx_file
    return ''


def delete_file(file_name):
    '''删除资源文件'''
    file_export_path = find_file(file_name, path_type='export')
    file_show_path = find_file(file_name, path_type='show')
    if file_export_path == '' or file_show_path == '':
        return False
    os.remove(file_export_path)
    os.remove(file_show_path)
    return True


'''
---------------------------------华丽的分割线----------------------------------
'''


def get_menu_list():
    '''获取怕[os列表，数据库列表]'''
    _conf_Data = Conf_Xml_Data(''.join([_script_path, 'conf.xml']))
    return [_conf_Data.get_os_list(), _conf_Data.get_app_list()]


def get_trow_list(os_type='', app_name=''):
    '''根据过滤条件获取script列表信息'''

    def get_format(desc):
        '''描述信息格式化'''
        lines = desc.split('\n')
        new_desc = ''
        for line in lines:
            new_desc = ''.join([new_desc, line.strip(), '\n'])
        return new_desc.strip()

    def get_description(desc):
        '''只获取不多于80个字符的描述信息'''
        return desc if len(desc) < 80 else ''.join([desc[:80],'...'])

    trow_list = []
    _conf_Data = Conf_Xml_Data(''.join([_script_path, 'conf.xml']))
    script_list = _conf_Data.get_scripts(os_type=os_type, app_name=app_name)
    for script_name, description, script_path in script_list:
        '''获取[脚本名, 获取脚本目录路径, 获取描述信息, 获取tooltip描述信息]'''
        description = get_format(description)
        trow_list.append([script_name, script_path, get_description(description), description])
    return trow_list


def add_zip(filename_list):
    '''将文件列表打包成zip压缩包'''
    f = zipfile.ZipFile(''.join([_script_path, 'scripts.zip']), 'w', zipfile.ZIP_DEFLATED)
    for fileinfo in filename_list:
        rel_filename, filename = fileinfo.split('*')
        f.write(''.join([_script_path, rel_filename]), rel_filename)
        #f.write(''.join([_script_path, rel_filename]), filename)
    f.close()
    return ''.join([_script_path, 'scripts.zip'])


def read_file_block(fn, buf_size=10240):
    '''文件分块读取返回'''
    with open(fn, 'rb') as f:
        while 1:
            block = f.read(buf_size)
            if block:
                yield block
            else:
                break
