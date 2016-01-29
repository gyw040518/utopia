# coding: utf-8
from __future__ import division
import xlsxwriter
from django.db.models import AutoField
from utopia.api import *
from upgray.models import Rule, System, RULE_STATUS, SystemRecord, RuleRecord


from utopia.settings import *
import redis as RedisConnect

def redisconnect():
    res = RedisConnect.Redis(host=REDIS_HOST,port=REDIS_PORT,db=0)
    return res


def db_add_rule(**kwargs):
    """
    add a rule in database
    数据库中添加规则
    """
    name = kwargs.get('name')
    rule = get_object(Rule, name=name)

    if not rule:
        rule = Rule(**kwargs)
        rule.save()


def db_update_rule(**kwargs):
    """
    add a rule in database
    数据库中更新规则
    """
    rule_id = kwargs.pop('id')
    rule = get_object(Rule, id=rule_id)

    Rule.objects.filter(id=rule_id).update(**kwargs)

def rule_diff(before, after):
    """
    system change before and after
    """
    alter_dic = {}
    before_dic, after_dic = before, dict(after.iterlists())
    for k, v in before_dic.items():
        after_dic_values = after_dic.get(k, [])
        after_dic_value = after_dic_values[0] if len(after_dic_values) > 0 else u''
        uv = unicode(v) if v is not None else u''
        if uv != after_dic_value:
            alter_dic.update({k: [uv, after_dic_value]})

    for k, v in alter_dic.items():
        if v == [None, u'']:
            alter_dic.pop(k)

    return alter_dic



def rule_diff_one(before, after):
    print before.__dict__, after.__dict__
    fields = Rule._meta.get_all_field_names()
    for field in fields:
        print before.field, after.field


def db_rule_alert(rule, alert_dic):
    """
    rule alert info to db
    """
    alert_list = []
    rule_tuple_dic = {'status': RULE_STATUS}
    for field, value in alert_dic.iteritems():
        field_name = Rule._meta.get_field_by_name(field)[0].verbose_name

        if field in ['status']:
            alert_info = get_tuple_diff(rule_tuple_dic.get(field), field_name, value)
        elif field == 'use_default_auth':
            if unicode(value[0]) == 'True' and unicode(value[1]) == 'on' or \
                                    unicode(value[0]) == 'False' and unicode(value[1]) == '':
                continue
            else:
                name = rule.name
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
        RuleRecord.objects.create(rule=rule, content=alert_list)


def db_system_add(**kwargs):
    """
    add system to db
    添加系统时数据库操作函数
    """
    rule_id_list = kwargs.pop('rules')
    system = System(**kwargs)
    system.save()

    rule_select = []
    for rule_id in rule_id_list:
        rule = Rule.objects.filter(id=rule_id)
        rule_select.extend(rule)
    system.rule_name = rule_select


def db_system_update(**kwargs):
    """ 修改系统时数据库操作函数 """
    system_id = kwargs.pop('id')
    System.objects.filter(id=system_id).update(**kwargs)


def get_tuple_name(app_tuple, value):
    """"""
    for t in app_tuple:
        if t[0] == value:
            return t[1]

    return ''


def get_tuple_diff(system_tuple, field_name, value):
    """"""
    old_name = get_tuple_name(system_tuple, int(value[0])) if value[0] else u''
    new_name = get_tuple_name(system_tuple, int(value[1])) if value[1] else u''
    alert_info = [field_name, old_name, new_name]
    return alert_info


def system_diff(before, after):
    """
    system change before and after
    """
    alter_dic = {}
    before_dic, after_dic = before, dict(after.iterlists())
    for k, v in before_dic.items():
        after_dic_values = after_dic.get(k, [])
        if k == 'rule':
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


def system_diff_one(before, after):
    print before.__dict__, after.__dict__
    fields = System._meta.get_all_field_names()
    for field in fields:
        print before.field, after.field


def db_system_alert(system, alert_dic):
    """
    system alert info to db
    """
    alert_list = []
    system_tuple_dic = {'status': RULE_STATUS}
    for field, value in alert_dic.iteritems():
        field_name = System._meta.get_field_by_name(field)[0].verbose_name

        if field in ['status']:
            alert_info = get_tuple_diff(system_tuple_dic.get(field), field_name, value)

        elif field == 'rule_name':
            old, new = [], []
            for rule_id in value[0]:
                rule_name = Rule.objects.get(id=int(rule_id)).name
                old.append(rule_name)
            for rule_id in value[1]:
                rule_name = Rule.objects.get(id=int(rule_id)).name
                new.append(rule_name)
            if sorted(old) == sorted(new):
                continue
            else:
                alert_info = [field_name, ','.join(old), ','.join(new)]
        elif field == 'use_default_auth':
            if unicode(value[0]) == 'True' and unicode(value[1]) == 'on' or \
                                    unicode(value[0]) == 'False' and unicode(value[1]) == '':
                continue
            else:
                name = system.name
                alert_info = [field_name, u'默认', name] if unicode(value[0]) == 'True' else \
                    [field_name, name, u'默认']
        else:
            alert_info = [field_name, unicode(value[0]), unicode(value[1])]

        if 'alert_info' in dir():
            alert_list.append(alert_info)

    if alert_list:
        SystemRecord.objects.create(system=system, content=alert_list)


def write_rule_excel(rule_all):
    data = []
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = 'cmdb_excel_' + now + '.xlsx'
    workbook = xlsxwriter.Workbook('static/files/excels/%s' % file_name)
    worksheet = workbook.add_worksheet(u'CMDB数据')
    worksheet.set_first_sheet()
    worksheet.set_column('A:E', 15)
    worksheet.set_column('F:F', 40)
    worksheet.set_column('G:Z', 15)
    title = [u'规则名称', u'规则简称', u'规则内容',
              u'规则状态', u'备注']
    for rule in rule_all:
        status = rule.get_status_display()

        alter_dic = [rule.name, rule.shortname, rule.content,
                    status,rule.comment]
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



def write_system_excel(system_all):
    data = []
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = 'cmdb_excel_' + now + '.xlsx'
    workbook = xlsxwriter.Workbook('static/files/excels/%s' % file_name)
    worksheet = workbook.add_worksheet(u'CMDB数据')
    worksheet.set_first_sheet()
    worksheet.set_column('A:E', 15)
    worksheet.set_column('F:F', 40)
    worksheet.set_column('G:Z', 15)
    title = [u'系统名称', u'规则名称',
             u'A版本流量', u'B版本流量', u'系统状态', u'备注']
    for system in system_all:
        rule_name = system.rule_name.name
        status = system.get_status_display()
        alter_dic = [system.name, rule_name, system.old_version, system.new_version,
                     status, system.comment]
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


def ansible_record(system, ansible_dic):
    alert_dic = {}
    system_dic = system.__dict__
    for field, value in ansible_dic.items():
        old = system_dic.get(field)
        new = ansible_dic.get(field)
        if unicode(old) != unicode(new):
            setattr(system, field, value)
            system.save()
            alert_dic[field] = [old, new]

    db_system_alert(system, alert_dic)
