#-*-coding:utf-8-*-
'''
根据当前页和总页数来实现带有省略号的页码列表
'''

p_around = 3#当前页左右显示条目数
p_boundary = 2#首尾至少要显示的条目数
p_nosuspoint = 2 * (p_around + p_boundary)#不显示省略号的最大条目数

def get_page_list(current_index, total_pages):
    '''输入当前页码与总页码，返回页码列表'''
    pages = []
    head_list = range(1, p_boundary + 1)#头显示页列表
    tail_list = range(total_pages - p_boundary + 1, total_pages + 1)#尾显示页列表

    if total_pages <= p_nosuspoint:
        for page in range(1, total_pages + 1):
            pages.append(str(page))
    else:
        left_suspoint = False  # 当前页左边是否存在省略号
        right_suspoint = False  # 当前页右边是否存在省略号
        if current_index - 1 > p_around + p_boundary:
            '''当前页与首页的差大于头显示页数与左边显示页数的和'''
            left_suspoint = True
        if total_pages - current_index > p_around + p_boundary:
            '''当尾页与当前页的差大于尾显示页数与右边显示页数的和'''
            right_suspoint = True
        if left_suspoint:
            '''添加头显示页、省略号和左边显示页到列表'''
            for index in head_list:
                pages.append(str(index))
            pages.append('...')
            for index in range(p_around):
                pages.append(str(current_index - p_around + index))

            if current_index in tail_list:
                '''判断当前页是否在尾显示页中'''
                for index in tail_list:
                    if current_index == index:
                        pages.append(str(current_index))
                        break
        else:
            '''添加当前页左侧所有页到列表'''
            pages.extend(str(page) for page in range(1, current_index))
        if current_index not in head_list and current_index not in tail_list:
            '''如果当前页不在头尾显示页中，则添加当前显示页到列表'''
            pages.append(str(current_index))
        if right_suspoint:
            if current_index in head_list:
                '''判断当前页是否在头显示页中'''
                for index in head_list:
                    if current_index == index:
                        pages.append(str(current_index))
                        break
            '''添加右侧显示页、省略号和尾显示页到列表'''
            for index in range(p_around):
                pages.append(str(current_index + index + 1))
            pages.append('...')
            for index in tail_list:
                pages.append(str(index))
        else:
            '''添加当前页、右侧所有页到列表'''
            pages.extend(str(page) for page in range(current_index + 1, total_pages + 1))
    return pages

