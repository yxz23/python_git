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


def get_left_data():
    '''返回左侧页面所需数据列表'''
    info_dict = {'sys': []}
    for info in Upload_Table.objects.all():
        info_dict['sys'].append((info.ShowName, info.UserName))
    return info_dict


def get_right_data(data_info):
    '''data_info 格式：sys_fileName_currentPage'''
    info_list = data_info.encode('utf-8').replace('/', '').split('_')
    table_name = '_'.join(info_list[1 : -1]).strip('_')#获取表名
    current_page = int(info_list[-1])#获取当前页码
    file_name = ''.join([_file_path, '/', table_name, '.csv']).decode('utf-8')
    with open(file_name) as f_info:
        head_info = f_info.readline()  # 表头信息
        head_info = head_info.strip().split('\t')
        body_info = [val.strip().split('\t') for val in f_info.readlines()]#表内容信息
        tbody_info = body_info[(current_page - 1) * _page_step : current_page * _page_step]#截取一页表内表内容

    table_data = table_name, head_info, tbody_info#(表名，表头信息列表，表内容信息列表)
    page_data = get_page_data(len(body_info), data_info)#根据总记录数和当前页信息获取页码html

    return table_data, page_data


def get_page_data(record_count, data_info):
    '''获取页码列表页所需数据(链接对应url，当前页码，页码列表)'''
    info_list = data_info.encode('utf-8').replace('/', '').split('_')
    current_page = int(info_list[-1])
    file_url = '_'.join(info_list[:-1])
    page_list = get_page_list(current_page, int(ceil(record_count / float(_page_step))))
    return file_url, str(current_page), page_list


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
