# coding: utf-8
from __future__ import division
import xlrd
import xlsxwriter
from django.db.models import AutoField
from utopia.api import *
from upapp.models import APP_STATUS, APP_TYPE, AppRecord, App, AppGroup
from upenv.models import ENV_ENVS
from upperm.ansible_api import MyRunner
from upperm.perm_api import gen_resource
from utopia.templatetags.mytags import get_disk_info


def group_add_app(group, app_id=None, app_value=None):
    """
    应用组添加应用
    App group add a app
    """
    if app_id:
        app = get_object(App, id=app_id)
    else:
        app = get_object(App, value=app_value)

    if app:
        group.app_set.add(app)


def db_add_group(**kwargs):
    """
    add a app group in database
    数据库中添加应用
    """
    name = kwargs.get('name')
    group = get_object(AppGroup, name=name)
    app_id_list = kwargs.pop('app_select')

    if not group:
        group = AppGroup(**kwargs)
        group.save()
        for app_id in app_id_list:
            group_add_app(group, app_id)


def db_update_group(**kwargs):
    """
    add a app group in database
    数据库中更新应用
    """
    group_id = kwargs.pop('id')
    app_id_list = kwargs.pop('app_select')
    group = get_object(AppGroup, id=group_id)

    for app_id in app_id_list:
        group_add_app(group, app_id)

    AppGroup.objects.filter(id=group_id).update(**kwargs)


def db_app_add(**kwargs):
    """
    add app to db
    添加应用时数据库操作函数
    """
    group_id_list = kwargs.pop('groups')
    app = App(**kwargs)
    app.save()

    group_select = []
    for group_id in group_id_list:
        group = AppGroup.objects.filter(id=group_id)
        group_select.extend(group)
    app.group = group_select


def db_app_update(**kwargs):
    """ 修改应用时数据库操作函数 """
    app_id = kwargs.pop('id')
    App.objects.filter(id=app_id).update(**kwargs)


def get_tuple_name(app_tuple, value):
    """"""
    for t in app_tuple:
        if t[0] == value:
            return t[1]

    return ''


def get_tuple_diff(app_tuple, field_name, value):
    """"""
    old_name = get_tuple_name(app_tuple, int(value[0])) if value[0] else u''
    new_name = get_tuple_name(app_tuple, int(value[1])) if value[1] else u''
    alert_info = [field_name, old_name, new_name]
    return alert_info


def app_diff(before, after):
    """
    app change before and after
    """
    alter_dic = {}
    before_dic, after_dic = before, dict(after.iterlists())
    for k, v in before_dic.items():
        after_dic_values = after_dic.get(k, [])
        if k == 'group':
            after_dic_value = after_dic_values if len(after_dic_values) > 0 else u''
            uv = v if v is not None else u''
        else:
            after_dic_value = after_dic_values[0] if len(after_dic_values) > 0 else u''
            uv = unicode(v) if v is not None else u''
        if uv != after_dic_value:
            alter_dic.update({k: [uv, after_dic_value]})

    for k, v in alter_dic.items():
        if v == [None, u'']:
            alter_dic.pop(k)

    return alter_dic


def app_diff_one(before, after):
    print before.__dict__, after.__dict__
    fields = App._meta.get_all_field_names()
    for field in fields:
        print before.field, after.field


def db_app_alert(app, alert_dic):
    """
    app alert info to db
    """
    alert_list = []
    app_tuple_dic = {'status': APP_STATUS, 'app_type': APP_TYPE}
    for field, value in alert_dic.iteritems():
        field_name = App._meta.get_field_by_name(field)[0].verbose_name

        if field in ['status', 'app_type']:
            alert_info = get_tuple_diff(app_tuple_dic.get(field), field_name, value)

        elif field == 'group':
            old, new = [], []
            for group_id in value[0]:
                group_name = AppGroup.objects.get(id=int(group_id)).name
                old.append(group_name)
            for group_id in value[1]:
                group_name = AppGroup.objects.get(id=int(group_id)).name
                new.append(group_name)
            if sorted(old) == sorted(new):
                continue
            else:
                alert_info = [field_name, ','.join(old), ','.join(new)]
        elif field == 'use_default_auth':
            if unicode(value[0]) == 'True' and unicode(value[1]) == 'on' or \
                                    unicode(value[0]) == 'False' and unicode(value[1]) == '':
                continue
            else:
                name = app.name
                alert_info = [field_name, u'默认', name] if unicode(value[0]) == 'True' else \
                    [field_name, name, u'默认']

        elif field == 'is_active':
            if unicode(value[0]) == 'True' and unicode(value[1]) == '1' or \
                                    unicode(value[0]) == 'False' and unicode(value[1]) == '0':
                continue
            else:
                alert_info = [u'是否激活', u'激活', u'禁用'] if unicode(value[0]) == 'True' else \
                    [u'是否激活', u'禁用', u'激活']

        else:
            alert_info = [field_name, unicode(value[0]), unicode(value[1])]

        if 'alert_info' in dir():
            alert_list.append(alert_info)

    if alert_list:
        AppRecord.objects.create(app=app, content=alert_list)


def write_excel(app_all):
    data = []
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = 'cmdb_excel_' + now + '.xlsx'
    workbook = xlsxwriter.Workbook('static/files/excels/%s' % file_name)
    worksheet = workbook.add_worksheet(u'CMDB数据')
    worksheet.set_first_sheet()
    worksheet.set_column('A:E', 15)
    worksheet.set_column('F:F', 40)
    worksheet.set_column('G:Z', 15)
    title = [u'应用名称', u'应用组', 
             u'应用类型', u'应用状态', u'备注']
    for app in app_all:
        group_list = []
        for p in app.group.all():
            group_list.append(p.name)

        group_all = '/'.join(group_list)
        status = app.get_status_display()

        alter_dic = [app.name, group_all, 
                     status, app.comment]
        data.append(alter_dic)
    format = workbook.add_format()
    format.set_border(1)
    format.set_align('center')
    format.set_align('vcenter')
    format.set_text_wrap()

    format_title = workbook.add_format()
    format_title.set_border(1)
    format_title.set_bg_color('#cccccc')
    format_title.set_align('center')
    format_title.set_bold()

    format_ave = workbook.add_format()
    format_ave.set_border(1)
    format_ave.set_num_format('0.00')

    worksheet.write_row('A1', title, format_title)
    i = 2
    for alter_dic in data:
        location = 'A' + str(i)
        worksheet.write_row(location, alter_dic, format)
        i += 1

    workbook.close()
    ret = (True, file_name)
    return ret


def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and \
                    not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


def ansible_record(app, ansible_dic):
    alert_dic = {}
    app_dic = app.__dict__
    for field, value in ansible_dic.items():
        old = app_dic.get(field)
        new = ansible_dic.get(field)
        if unicode(old) != unicode(new):
            setattr(app, field, value)
            app.save()
            alert_dic[field] = [old, new]

    db_app_alert(app, alert_dic)


def excel_to_db(excel_file):
    """
    App add batch function
    """
    try:
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
    except Exception, e:
        return False
    else:
        table = data.sheets()[0]
        rows = table.nrows
        for row_num in range(1, rows):
            row = table.row_values(row_num)
            if row:
                group_instance = []
                value, name, use_default_auth, group = row
                if get_object(App, name=name):
                    continue
                use_default_auth = 1 if use_default_auth == u'默认' else 0
                if name:
                    app = App(value=value,
                                  name=name,
                                  use_default_auth=use_default_auth
                                  )
                    app.save()
                    group_list = group.split('/')
                    for group_name in group_list:
                        group = get_object(AppGroup, name=group_name)
                        if group:
                            group_instance.append(group)
                    if group_instance:
                        app.group = group_instance
                    app.save()
        return True
