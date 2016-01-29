# coding:utf-8

from django.db.models import Q
from upetcd.etcd_api import *
from utopia.api import *
from utopia.models import Setting
from upetcd.forms import EtcdForm
from upetcd.models import Etcd, EtcdGroup, ETCD_TYPE, ETCD_STATUS
from upperm.perm_api import get_group_asset_perm, get_group_user_perm


@require_role('admin')
def group_add(request):
    """
    Group add view
    添加参数组
    """
    header_title, path1, path2 = u'添加参数组', u'参数管理', u'添加参数组'
    etcd_all = Etcd.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '')
        etcd_select = request.POST.getlist('etcd_select', [])
        comment = request.POST.get('comment', '')

        try:
            if not name:
                emg = u'组名不能为空'
                raise ServerError(emg)

            etcd_group_test = get_object(EtcdGroup, name=name)
            if etcd_group_test:
                emg = u"该组名 %s 已存在" % name
                raise ServerError(emg)

        except ServerError:
            pass

        else:
            db_add_group(name=name, comment=comment, etcd_select=etcd_select)
            smg = u"参数组 %s 添加成功" % name

    return my_render('upetcd/group_add.html', locals(), request)


@require_role('admin')
def group_edit(request):
    """
    Group edit view
    编辑参数组
    """
    header_title, path1, path2 = u'编辑参数组', u'参数管理', u'编辑参数组'
    group_id = request.GET.get('id', '')
    group = get_object(EtcdGroup, id=group_id)

    etcd_all = Etcd.objects.all()
    etcd_select = Etcd.objects.filter(group=group)
    etcd_no_select = [a for a in etcd_all if a not in etcd_select]

    if request.method == 'POST':
        name = request.POST.get('name', '')
        etcd_select = request.POST.getlist('etcd_select', [])
        comment = request.POST.get('comment', '')

        try:
            if not name:
                emg = u'组名不能为空'
                raise ServerError(emg)

            if group.name != name:
                etcd_group_test = get_object(EtcdGroup, name=name)
                if etcd_group_test:
                    emg = u"该组名 %s 已存在" % name
                    raise ServerError(emg)

        except ServerError:
            pass

        else:
            group.etcd_set.clear()
            db_update_group(id=group_id, name=name, comment=comment, etcd_select=etcd_select)
            smg = u"参数组 %s 添加成功" % name

        return HttpResponseRedirect(reverse('etcd_group_list'))

    return my_render('upetcd/group_edit.html', locals(), request)


@require_role('admin')
def group_list(request):
    """
    list etcd group
    列出参数组
    """
    header_title, path1, path2 = u'查看参数组', u'参数管理', u'查看参数组'
    keyword = request.GET.get('keyword', '')
    etcd_group_list = EtcdGroup.objects.all()
    group_id = request.GET.get('id')
    if group_id:
        etcd_group_list = etcd_group_list.filter(id=group_id)
    if keyword:
        etcd_group_list = etcd_group_list.filter(Q(name__contains=keyword) | Q(comment__contains=keyword))

    etcd_group_list, p, etcd_groups, page_range, current_page, show_first, show_end = pages(etcd_group_list, request)
    return my_render('upetcd/group_list.html', locals(), request)


@require_role('admin')
def group_del(request):
    """
    Group delete view
    删除参数组
    """
    group_ids = request.GET.get('id', '')
    group_id_list = group_ids.split(',')

    for group_id in group_id_list:
        EtcdGroup.objects.filter(id=group_id).delete()

    return HttpResponse(u'删除成功')


@require_role('admin')
def etcd_add(request):
    """
    Etcd add view
    添加参数
    """
    header_title, path1, path2 = u'添加参数', u'参数管理', u'添加参数'
    etcd_group_all = EtcdGroup.objects.all()
    af = EtcdForm()
    default_setting = get_object(Setting, name='default')
    if request.method == 'POST':
        af_post = EtcdForm(request.POST)
        value = request.POST.get('value', '')
        name = request.POST.get('name', '')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if Etcd.objects.filter(name=str(name)):
                error = u'该参数名 %s 已存在!' % name
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                etcd_save = af_post.save(commit=False)
                if not value:
                    etcd_save.value = name
                etcd_save.is_active = True if is_active else False
                etcd_save.save()
                af_post.save_m2m()

                msg = u'参数 %s 添加成功' % name
            else:
                esg = u'参数 %s 添加失败' % name

    return my_render('upetcd/etcd_add.html', locals(), request)


@require_role('admin')
def etcd_add_batch(request):
    header_title, path1, path2 = u'添加参数', u'参数管理', u'批量添加'
    return my_render('upetcd/etcd_add_batch.html', locals(), request)


@require_role('admin')
def etcd_del(request):
    """
    del a etcd
    删除参数
    """
    etcd_id = request.GET.get('id', '')
    if etcd_id:
        Etcd.objects.filter(id=etcd_id).delete()

    if request.method == 'POST':
        etcd_batch = request.GET.get('arg', '')
        etcd_id_all = str(request.POST.get('etcd_id_all', ''))

        if etcd_batch:
            for etcd_id in etcd_id_all.split(','):
                etcd = get_object(Etcd, id=etcd_id)
                etcd.delete()

    return HttpResponse(u'删除成功')


@require_role(role='super')
def etcd_edit(request):
    """
    edit a etcd
    修改参数
    """
    header_title, path1, path2 = u'修改参数', u'参数管理', u'修改参数'

    etcd_id = request.GET.get('id', '')
    etcd = get_object(Etcd, id=etcd_id)
    af = EtcdForm(instance=etcd)
    if request.method == 'POST':
        af_post = EtcdForm(request.POST, instance=etcd)
        value = request.POST.get('value', '')
        name = request.POST.get('name', '')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            etcd_test = get_object(Etcd, name=name)
            if etcd_test and etcd_id != unicode(etcd_test.id):
                emg = u'该参数名 %s 已存在!' % name
                raise ServerError(emg)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.is_active = True if is_active else False
                af_save.save()
                af_post.save_m2m()
                info = etcd_diff(af_post.__dict__.get('initial'), request.POST)
                smg = u'参数 %s 修改成功' % value
            else:
                emg = u'参数 %s 修改失败' % value
                return my_render('upetcd/error.html', locals(), request)
            return HttpResponseRedirect(reverse('etcd_detail')+'?id=%s' % etcd_id)

    return my_render('upetcd/etcd_edit.html', locals(), request)


@require_role('user')
def etcd_list(request):
    """
    etcd list view
    """
    header_title, path1, path2 = u'查看参数', u'参数管理', u'查看参数'
    username = request.user.username
    user_perm = request.session['role_id']
    etcd_group_all = EtcdGroup.objects.all()
    etcd_types = ETCD_TYPE
    etcd_envs = ENV_ENVS
    etcd_status = ETCD_STATUS
    group_name = request.GET.get('group', '')
    etcd_type = request.GET.get('etcd_type', '')
    etcd_env = request.GET.get('etcd_env', '')
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    group_id = request.GET.get("group_id", '')
    etcd_id_all = request.GET.getlist("id", '')

    if group_id:
        group = get_object(EtcdGroup, id=group_id)
        if group:
            etcd_find = Etcd.objects.filter(group=group)
    else:
        if user_perm != 0:
            etcd_find = Etcd.objects.all()
        else:
            etcd_id_all = []
            user = get_object(User, username=username)
            etcd_perm = get_group_user_perm(user) if user else {'etcd': ''}
            user_etcd_perm = etcd_perm['etcd'].keys()
            for etcd in user_etcd_perm:
                etcd_id_all.append(etcd.id)
            etcd_find = Etcd.objects.filter(pk__in=etcd_id_all)
            etcd_group_all = list(etcd_perm['etcd_group'])

    if etcd_env:
        etcd_find = etcd_find.filter(etcd_env__contains=etcd_env)

    if group_name:
        etcd_find = etcd_find.filter(group__name__contains=group_name)

    if etcd_type:
        etcd_find = etcd_find.filter(etcd_type__contains=etcd_type)

    if status:
        etcd_find = etcd_find.filter(status__contains=status)

    if keyword:
        etcd_find = etcd_find.filter(
            Q(name__contains=keyword) |
            Q(pre_value__contains=keyword) |
            Q(value__contains=keyword) |
            Q(comment__contains=keyword) |
            Q(group__name__contains=keyword))

    if export:
        if etcd_id_all:
            etcd_find = []
            for etcd_id in etcd_id_all:
                etcd = get_object(Etcd, id=etcd_id)
                if etcd:
                    etcd_find.append(etcd)
        s = write_excel(etcd_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upetcd/etcd_excel_download.html', locals(), request)
    etcds_list, p, etcds, page_range, current_page, show_first, show_end = pages(etcd_find, request)
    if user_perm != 0:
        return my_render('upetcd/etcd_list.html', locals(), request)
    else:
        return my_render('upetcd/etcd_cu_list.html', locals(), request)


@require_role('admin')
def etcd_edit_batch(request):
    af = EtcdForm()
    name = request.user.username
    etcd_group_all = EtcdGroup.objects.all()

    if request.method == 'POST':
        etcd_env = request.POST.get('etcd_env', '')
        group = request.POST.getlist('group', [])
        comment = request.POST.get('comment', '')
        use_default_auth = request.POST.get('use_default_auth', '')
        etcd_id_all = unicode(request.GET.get('etcd_id_all', ''))
        etcd_id_all = etcd_id_all.split(',')
        for etcd_id in etcd_id_all:
            alert_list = []
            etcd = get_object(Etcd, id=etcd_id)
            if etcd:
                if etcd_env:
                    if etcd.etcd_env != etcd_env:
                        etcd.etcd_env = etcd_env
                        alert_list.append([u'环境', etcd.etcd_env, etcd_env])

                if use_default_auth:
                    if use_default_auth == 'default':
                        etcd.use_default_auth = 1
                        alert_list.append([u'使用默认管理账号', etcd.use_default_auth, u'默认'])

                if group:
                    group_new, group_old, group_new_name, group_old_name = [], etcd.group.all(), [], []
                    for group_id in group:
                        g = get_object(EtcdGroup, id=group_id)
                        if g:
                            group_new.append(g)
                    if not set(group_new) < set(group_old):
                        group_instance = list(set(group_new) | set(group_old))
                        for g in group_instance:
                            group_new_name.append(g.name)
                        for g in group_old:
                            group_old_name.append(g.name)
                        etcd.group = group_instance
                        alert_list.append([u'参数组', ','.join(group_old_name), ','.join(group_new_name)])
                if comment:
                    if etcd.comment != comment:
                        etcd.comment = comment
                        alert_list.append([u'备注', etcd.comment, comment])
                etcd.save()

            if alert_list:
                recode_name = unicode(name) + ' - ' + u'批量'
                EtcdRecord.objects.create(etcd=etcd, username=recode_name, content=alert_list)
        return my_render('upetcd/etcd_update_status.html', locals(), request)

    return my_render('upetcd/etcd_edit_batch.html', locals(), request)


@require_role('admin')
def etcd_detail(request):
    """
    Etcd detail view
    """
    header_title, path1, path2 = u'参数详细信息', u'参数管理', u'参数详情'
    etcd_id = request.GET.get('id', '')
    etcd = get_object(Etcd, id=etcd_id)
    perm_info = get_group_asset_perm(etcd)
    log = Log.objects.filter(host=etcd.name)
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'role':
                user_group_perm = value
    print perm_info

    etcd_record = EtcdRecord.objects.filter(etcd=etcd).order_by('-alert_time')

    return my_render('upetcd/etcd_detail.html', locals(), request)


@require_role('admin')
def etcd_update(request):
    """
    Etcd update host info via ansible view
    """
    etcd_id = request.GET.get('id', '')
    etcd = get_object(Etcd, id=etcd_id)
    name = request.user.username
    if not etcd:
        return HttpResponseRedirect(reverse('etcd_detail')+'?id=%s' % etcd_id)
    else:
        etcd_ansible_update([etcd], name)
    return HttpResponseRedirect(reverse('etcd_detail')+'?id=%s' % etcd_id)


@require_role('admin')
def etcd_update_batch(request):
    if request.method == 'POST':
        arg = request.GET.get('arg', '')
        name = unicode(request.user.username) + ' - ' + u'自动更新'
        if arg == 'all':
            etcd_list = Etcd.objects.all()
        else:
            etcd_list = []
            etcd_id_all = unicode(request.POST.get('etcd_id_all', ''))
            etcd_id_all = etcd_id_all.split(',')
            for etcd_id in etcd_id_all:
                etcd = get_object(Etcd, id=etcd_id)
                if etcd:
                    etcd_list.append(etcd)
        etcd_ansible_update(etcd_list, name)
        return HttpResponse(u'批量更新成功!')
    return HttpResponse(u'批量更新成功!')


@require_role('admin')
def etcd_upload(request):
    """
    Upload etcd excel file view
    """
    if request.method == 'POST':
        excel_file = request.FILES.get('file_name', '')
        ret = excel_to_db(excel_file)
        if ret:
            smg = u'批量添加成功'
        else:
            emg = u'批量添加失败,请检查格式.'
    return my_render('upetcd/etcd_add_batch.html', locals(), request)
