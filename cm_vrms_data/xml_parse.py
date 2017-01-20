#-*-coding:utf-8-*-
'''
@File   : xml_parse.py
'''
import xml.dom.minidom as xdom

class Conf_Xml_Nodes(object):
    def __init__(self, xml_file):
        '''初始化文件根节点'''
        self.root_node = xdom.parse(xml_file).documentElement

    def get_os_nodes(self):
        return [os_node for os_node in self.root_node.getElementsByTagName('os')]

    def get_app_nodes(self, os_type=''):
        '''获取os节点下的所有app节点列表'''
        if os_type == '' or os_type is None:
            '''获取根节点下的所有app节点列表'''
            return self.root_node.getElementsByTagName('app')
        for os_node in self.get_os_nodes():
            if os_type == os_node.getAttribute('type'):
                return os_node.getElementsByTagName('app')
        return []

    def get_script_nodes(self, os_type='', app_name=''):
        '''(''代表“全部”，None代表“无”，其他为具体有效值)'''
        res_list = []
        if os_type == '' and app_name == '':
            '''获取文本中所有script节点'''
            res_list = self.root_node.getElementsByTagName('script')

        elif os_type == '' and app_name is None:
            '''获取所有os节点一级下的script节点'''
            for os_node in self.get_os_nodes():
                scripts_node = os_node.getElementsByTagName('script')
                res_list.extend([script_node for script_node in scripts_node if script_node.hasAttribute('type')])

        elif os_type == '' and app_name:
            '''获取所有os节点一级下的script节点 + app节点下script节点'''
            for os_node in self.get_os_nodes():
                scripts_node = os_node.getElementsByTagName('script')
                res_list.extend([script_node for script_node in scripts_node if script_node.hasAttribute('type')])
            for app_node in self.get_app_nodes(os_type):
                if app_name == app_node.getAttribute('name'):
                    res_list.extend(app_node.getElementsByTagName('script'))

        elif os_type is None and app_name == '':
            '''获取所有app节点下script节点'''
            for app_node in self.get_app_nodes(os_type):
                res_list.extend(app_node.getElementsByTagName('script'))

        elif os_type is None and app_name:
            '''获取app节点下的script节点'''
            for app_node in self.get_app_nodes(os_type):
                if app_name == app_node.getAttribute('name'):
                    res_list.extend(app_node.getElementsByTagName('script'))

        elif os_type and app_name == '':
            '''获取os_type节点下的所有script节点'''
            for os_node in self.get_os_nodes():
                if os_type == os_node.getAttribute('type'):
                    scripts_node = os_node.getElementsByTagName('script')
                    res_list.extend(script_node for script_node in scripts_node)

        elif os_type and app_name is None:
            '''获取os_type节点一级以下的script节点'''
            for os_node in self.get_os_nodes():
                if os_type == os_node.getAttribute('type'):
                    scripts_node = os_node.getElementsByTagName('script')
                    res_list.extend(script_node for script_node in scripts_node if script_node.hasAttribute('type'))

        elif os_type and app_name:
            '''获取os_type节点一级以下的script节点 + app节点下的script节点'''
            for os_node in self.get_os_nodes():
                if os_type == os_node.getAttribute('type'):
                    scripts_node = os_node.getElementsByTagName('script')
                    res_list.extend(script_node for script_node in scripts_node if script_node.hasAttribute('type'))

                    for app_node in self.get_app_nodes(os_type):
                        if app_name == app_node.getAttribute('name'):
                            res_list.extend(app_node.getElementsByTagName('script'))
        return res_list

    def get_script_path(self, script_node):
        '''获取脚本节点的路径'''
        p1_node = script_node.parentNode
        item1 = p1_node.getAttribute('type')
        if item1:
            return item1
        item1 = p1_node.getAttribute('name')
        item2 = p1_node.parentNode.getAttribute('type')
        return '{}_{}'.format(item2, item1)


class Conf_Xml_Data(object):
    def __init__(self, xml_file):
        self.conf_xml = Conf_Xml_Nodes(xml_file)

    def get_os_list(self):
        '''获取os类型列表'''
        os_nodes = self.conf_xml.get_os_nodes()
        return [os_node.getAttribute('type') for os_node in os_nodes]

    def get_app_list(self, os_type=''):
        '''获取app类型列表'''
        app_nodes = self.conf_xml.get_app_nodes(os_type)
        app_list = []
        for app_node in app_nodes:
            app_name = app_node.getAttribute('name')
            if app_name not in app_list:
                app_list.append(app_name)
        return app_list

    def get_scripts(self, os_type='', app_name=''):
        '''获取script信息列表[文件名，文件描述，文件节点路径]'''
        script_nodes = self.conf_xml.get_script_nodes(os_type, app_name)
        return [[script_node.getAttribute('file'), script_node.childNodes[0].data, self.conf_xml.get_script_path(script_node)] \
                for script_node in script_nodes]


if __name__ == '__main__':
    conf_Xml = Conf_Xml_Data('media/scripts/conf.xml')
    print 'get all script info : '
    os_list = conf_Xml.get_os_list()
    print 'length :', len(os_list)
    for os_name in os_list:
        print os_name, '-->', conf_Xml.get_app_list(os_name)

