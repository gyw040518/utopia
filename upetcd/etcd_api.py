# coding: utf-8
from __future__ import division
import xlrd
import xlsxwriter
from django.db.models import AutoField
from utopia.api import *
from upetcd.models import ETCD_STATUS, ETCD_TYPE, EtcdRecord, Etcd, EtcdGroup
from upenv.models import ENV_ENVS
from upperm.ansible_api import MyRunner
from upperm.perm_api import gen_resource
from utopia.templatetags.mytags import get_disk_info

from utopia.settings import *
import etcd as EtcdConnect

def etcdconnect():
    res = EtcdConnect.Client(host=((ETCD1_HOST, ETCD_PORT), (ETCD2_HOST, ETCD_PORT), (ETCD3_HOST, ETCD_PORT)), protocol='http', allow_reconnect=True, version_prefix='/v2' )
    return res


def group_add_etcd(group, etcd_id=None, etcd_value=None):
    """
    参数组添加参数
    Etcd group add a etcd
    """
    if etcd_id:
        etcd = get_object(Etcd, id=etcd_id)
    else:
        etcd = get_object(Etcd, value=etcd_value)

    if etcd:
        group.etcd_set.add(etcd)


def db_add_group(**kwargs):
    """
    add a etcd group in database
    数据库中添加参数
    """
    name = kwargs.get('name')
    group = get_object(EtcdGroup, name=name)
    etcd_id_list = kwargs.pop('etcd_select')

    if not group:
        group = EtcdGroup(**kwargs)
        group.save()
        for etcd_id in etcd_id_list:
            group_add_etcd(group, etcd_id)


def db_update_group(**kwargs):
    """
    add a etcd group in database
    数据库中更新参数
    """
    group_id = kwargs.pop('id')
    etcd_id_list = kwargs.pop('etcd_select')
    group = get_object(EtcdGroup, id=group_id)

    for etcd_id in etcd_id_list:
        group_add_etcd(group, etcd_id)

    EtcdGroup.objects.filter(id=group_id).update(**kwargs)


def db_etcd_add(**kwargs):
    """
    add etcd to db
    添加参数时数据库操作函数
    """
    group_id_list = kwargs.pop('groups')
    etcd = Etcd(**kwargs)
    etcd.save()

    group_select = []
    for group_id in group_id_list:
        group = EtcdGroup.objects.filter(id=group_id)
        group_select.extend(group)
    etcd.group = group_select


def db_etcd_update(**kwargs):
    """ 修改参数时数据库操作函数 """
    etcd_id = kwargs.pop('id')
    Etcd.objects.filter(id=etcd_id).update(**kwargs)


def sort_value_list(value_list):
    """ 参数值排序 """
    value_list.sort(key=lambda s: map(str, s.split('.')))
    return value_list


def get_tuple_name(etcd_tuple, value):
    """"""
    for t in etcd_tuple:
        if t[0] == value:
            return t[1]

    return ''


def get_tuple_diff(etcd_tuple, field_name, value):
    """"""
    old_name = get_tuple_name(etcd_tuple, int(value[0])) if value[0] else u''
    new_name = get_tuple_name(etcd_tuple, int(value[1])) if value[1] else u''
    alert_info = [field_name, old_name, new_name]
    return alert_info


def etcd_diff(before, after):
    """
    etcd change before and after
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


def etcd_diff_one(before, after):
    print before.__dict__, after.__dict__
    fields = Etcd._meta.get_all_field_names()
    for field in fields:
        print before.field, after.field


def db_etcd_alert(etcd, alert_dic):
    """
    etcd alert info to db
    """
    alert_list = []
    etcd_tuple_dic = {'status': ETCD_STATUS, 'etcd_env': ENV_ENVS, 'etcd_type': ETCD_TYPE}
    for field, value in alert_dic.iteritems():
        field_name = Etcd._meta.get_field_by_name(field)[0].verbose_name

        if field in ['status', 'etcd_env', 'etcd_type']:
            alert_info = get_tuple_diff(etcd_tuple_dic.get(field), field_name, value)

        elif field == 'group':
            old, new = [], []
            for group_id in value[0]:
                group_name = EtcdGroup.objects.get(id=int(group_id)).name
                old.append(group_name)
            for group_id in value[1]:
                group_name = EtcdGroup.objects.get(id=int(group_id)).name
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
                name = etcd.name
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
        EtcdRecord.objects.create(etcd=etcd, content=alert_list)


def write_excel(etcd_all):
    data = []
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = 'cmdb_excel_' + now + '.xlsx'
    workbook = xlsxwriter.Workbook('static/files/excels/%s' % file_name)
    worksheet = workbook.add_worksheet(u'CMDB数据')
    worksheet.set_first_sheet()
    worksheet.set_column('A:E', 15)
    worksheet.set_column('F:F', 40)
    worksheet.set_column('G:Z', 15)
    title = [u'参数名', u'参数值', u'所属参数组', 
             u'原参数', u'参数状态', u'备注']
    for etcd in etcd_all:
        group_list = []
        for p in etcd.group.all():
            group_list.append(p.name)

        group_all = '/'.join(group_list)
        status = etcd.get_status_display()

        alter_dic = [etcd.name, etcd.value, group_all, etcd.pre_value,
                     status, etcd.comment]
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


def ansible_record(etcd, ansible_dic):
    alert_dic = {}
    etcd_dic = etcd.__dict__
    for field, value in ansible_dic.items():
        old = etcd_dic.get(field)
        new = ansible_dic.get(field)
        if unicode(old) != unicode(new):
            setattr(etcd, field, value)
            etcd.save()
            alert_dic[field] = [old, new]

    db_etcd_alert(etcd, alert_dic)


def excel_to_db(excel_file):
    """
    Etcd add batch function
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
                if get_object(Etcd, name=name):
                    continue
                use_default_auth = 1 if use_default_auth == u'默认' else 0
                if name:
                    etcd = Etcd(value=value,
                                  name=name,
                                  use_default_auth=use_default_auth
                                  )
                    etcd.save()
                    group_list = group.split('/')
                    for group_name in group_list:
                        group = get_object(EtcdGroup, name=group_name)
                        if group:
                            group_instance.append(group)
                    if group_instance:
                        etcd.group = group_instance
                    etcd.save()
        return True

# def get_ansible_etcd_info(etcd_value, setup_info):
#     print etcd_value
#     pre_value = ','.join(pre_value_list) if pre_value_list else ''
#     etcd_info = [pre_value]
#     return etcd_info
#
# def etcd_ansible_update_all():
#     name = u'定时更新'
#     etcd_all = Etcd.objects.all()
#     etcd_ansible_update(etcd_all, name)

