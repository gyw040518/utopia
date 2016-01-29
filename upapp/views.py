# coding:utf-8

from django.db.models import Q
from upapp.app_api import *
from utopia.api import *
from utopia.models import Setting
from upasset.models import Asset
from upapp.forms import AppForm, MapForm
from upapp.models import App, AppGroup, APP_TYPE, APP_STATUS, Map, PROC_TYPE
from upperm.perm_api import get_group_asset_perm, get_group_user_perm



@require_role('admin')
def group_add(request):
    """
    Group add view
    添加应用组
    """
    header_title, path1, path2 = u'添加应用组', u'应用管理', u'添加应用组'
    app_all = App.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '')
        app_select = request.POST.getlist('app_select', [])
        comment = request.POST.get('comment', '')

        try:
            if not name:
                emg = u'组名不能为空'
                raise ServerError(emg)

            app_group = get_object(AppGroup, name=name)
            if app_group:
                emg = u"该组名 %s 已存在" % name
                raise ServerError(emg)

        except ServerError:
            pass

        else:
            db_add_group(name=name, comment=comment, app_select=app_select)
            smg = u"应用组 %s 添加成功" % name

    return my_render('upapp/group_add.html', locals(), request)


@require_role('admin')
def group_edit(request):
    """
    Group edit view
    编辑应用组
    """
    header_title, path1, path2 = u'编辑应用组', u'应用管理', u'编辑应用组'
    group_id = request.GET.get('id', '')
    group = get_object(AppGroup, id=group_id)

    app_all = App.objects.all()
    app_select = App.objects.filter(group=group)
    app_no_select = [a for a in app_all if a not in app_select]

    if request.method == 'POST':
        name = request.POST.get('name', '')
        app_select = request.POST.getlist('app_select', [])
        comment = request.POST.get('comment', '')

        try:
            if not name:
                emg = u'组名不能为空'
                raise ServerError(emg)

            if group.name != name:
                app_group = get_object(AppGroup, name=name)
                if app_group:
                    emg = u"该组名 %s 已存在" % name
                    raise ServerError(emg)

        except ServerError:
            pass

        else:
            group.app_set.clear()
            db_update_group(id=group_id, name=name, comment=comment, app_select=app_select)
            smg = u"应用组 %s 添加成功" % name

        return HttpResponseRedirect(reverse('app_group_list'))

    return my_render('upapp/group_edit.html', locals(), request)


@require_role('admin')
def group_list(request):
    """
    list app group
    列出应用组
    """
    header_title, path1, path2 = u'查看应用组', u'应用管理', u'查看应用组'
    keyword = request.GET.get('keyword', '')
    app_group_list = AppGroup.objects.all()
    group_id = request.GET.get('id')
    if group_id:
        app_group_list = app_group_list.filter(id=group_id)
    if keyword:
        app_group_list = app_group_list.filter(Q(name__contains=keyword) | Q(comment__contains=keyword))

    app_group_list, p, app_groups, page_range, current_page, show_first, show_end = pages(app_group_list, request)
    return my_render('upapp/group_list.html', locals(), request)


@require_role('admin')
def group_del(request):
    """
    Group delete view
    删除应用组
    """
    group_ids = request.GET.get('id', '')
    group_id_list = group_ids.split(',')

    for group_id in group_id_list:
        AppGroup.objects.filter(id=group_id).delete()

    return HttpResponse(u'删除成功')


@require_role('admin')
def app_add(request):
    """
    App add view
    添加应用
    """
    header_title, path1, path2 = u'添加应用', u'应用管理', u'添加应用'
    app_group_all = AppGroup.objects.all()
    af = AppForm()
    default_setting = get_object(Setting, name='default')
    if request.method == 'POST':
        af_post = AppForm(request.POST)
        name = request.POST.get('name', '')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if App.objects.filter(name=str(name)):
                error = u'该应用名称 %s 已存在!' % name
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                app_save = af_post.save(commit=False)
                app_save.is_active = True if is_active else False
                app_save.save()
                af_post.save_m2m()

                msg = u'应用 %s 添加成功' % name
            else:
                esg = u'应用 %s 添加失败' % name

    return my_render('upapp/app_add.html', locals(), request)


@require_role('admin')
def app_add_batch(request):
    header_title, path1, path2 = u'添加应用', u'应用管理', u'批量添加'
    return my_render('upapp/app_add_batch.html', locals(), request)


@require_role('admin')
def app_del(request):
    """
    del a app
    删除应用
    """
    app_id = request.GET.get('id', '')
    if app_id:
        App.objects.filter(id=app_id).delete()

    if request.method == 'POST':
        app_batch = request.GET.get('arg', '')
        app_id_all = str(request.POST.get('app_id_all', ''))

        if app_batch:
            for app_id in app_id_all.split(','):
                app = get_object(App, id=app_id)
                app.delete()

    return HttpResponse(u'删除成功')


@require_role(role='super')
def app_edit(request):
    """
    edit a app
    修改应用
    """
    header_title, path1, path2 = u'修改应用', u'应用管理', u'修改应用'

    app_id = request.GET.get('id', '')
    app = get_object(App, id=app_id)
    af = AppForm(instance=app)
    if request.method == 'POST':
        af_post = AppForm(request.POST, instance=app)
        name = request.POST.get('name', '')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            app_test = get_object(App, name=name)
            if app_test and app_id != unicode(app_test.id):
                emg = u'该应用名称 %s 已存在!' % name
                raise ServerError(emg)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.is_active = True if is_active else False
                af_save.save()
                af_post.save_m2m()
                info = app_diff(af_post.__dict__.get('initial'), request.POST)
                smg = u'应用 %s 修改成功' % name
            else:
                emg = u'应用 %s 修改失败' % name
                return my_render('upapp/error.html', locals(), request)
            return HttpResponseRedirect(reverse('app_detail')+'?id=%s' % app_id)

    return my_render('upapp/app_edit.html', locals(), request)


@require_role('user')
def app_list(request):
    """
    app list view
    """
    header_title, path1, path2 = u'查看应用', u'应用管理', u'查看应用'
    username = request.user.username
    user_perm = request.session['role_id']
    app_group_all = AppGroup.objects.all()
    app_types = APP_TYPE
    app_status = APP_STATUS
    group_name = request.GET.get('group', '')
    app_type = request.GET.get('app_type', '')
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    group_id = request.GET.get("group_id", '')
    app_id_all = request.GET.getlist("id", '')

    if group_id:
        group = get_object(AppGroup, id=group_id)
        if group:
            app_find = App.objects.filter(group=group)
    else:
        if user_perm != 0:
            app_find = App.objects.all()
        else:
            app_id_all = []
            user = get_object(User, username=username)
            app_perm = get_group_user_perm(user) if user else {'app': ''}
            user_app_perm = app_perm['app'].keys()
            for app in user_app_perm:
                app_id_all.append(app.id)
            app_find = App.objects.filter(pk__in=app_id_all)
            app_group_all = list(app_perm['app_group'])

    if group_name:
        app_find = app_find.filter(group__name__contains=group_name)

    if app_type:
        app_find = app_find.filter(app_type__contains=app_type)

    if status:
        app_find = app_find.filter(status__contains=status)

    if keyword:
        app_find = app_find.filter(
            Q(name__contains=keyword) |
            Q(comment__contains=keyword) |
            Q(group__name__contains=keyword))

    if export:
        if app_id_all:
            app_find = []
            for app_id in app_id_all:
                app = get_object(App, id=app_id)
                if app:
                    app_find.append(app)
        s = write_excel(app_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upapp/app_excel_download.html', locals(), request)
    apps_list, p, apps, page_range, current_page, show_first, show_end = pages(app_find, request)
    if user_perm != 0:
        return my_render('upapp/app_list.html', locals(), request)
    else:
        return my_render('upapp/app_cu_list.html', locals(), request)


@require_role('admin')
def app_edit_batch(request):
    af = AppForm()
    name = request.user.username
    app_group_all = AppGroup.objects.all()

    if request.method == 'POST':
        app_env = request.POST.get('app_env', '')
        group = request.POST.getlist('group', [])
        comment = request.POST.get('comment', '')
        use_default_auth = request.POST.get('use_default_auth', '')
        app_id_all = unicode(request.GET.get('app_id_all', ''))
        app_id_all = app_id_all.split(',')
        for app_id in app_id_all:
            alert_list = []
            app = get_object(App, id=app_id)
            if app:
                if use_default_auth:
                    if use_default_auth == 'default':
                        app.use_default_auth = 1
                        alert_list.append([u'使用默认管理账号', app.use_default_auth, u'默认'])

                if group:
                    group_new, group_old, group_new_name, group_old_name = [], app.group.all(), [], []
                    for group_id in group:
                        g = get_object(AppGroup, id=group_id)
                        if g:
                            group_new.append(g)
                    if not set(group_new) < set(group_old):
                        group_instance = list(set(group_new) | set(group_old))
                        for g in group_instance:
                            group_new_name.append(g.name)
                        for g in group_old:
                            group_old_name.append(g.name)
                        app.group = group_instance
                        alert_list.append([u'应用组', ','.join(group_old_name), ','.join(group_new_name)])
                if comment:
                    if app.comment != comment:
                        app.comment = comment
                        alert_list.append([u'备注', app.comment, comment])
                app.save()

            if alert_list:
                recode_name = unicode(name) + ' - ' + u'批量'
                AppRecord.objects.create(app=app, username=recode_name, content=alert_list)
        return my_render('upapp/app_update_status.html', locals(), request)

    return my_render('upapp/app_edit_batch.html', locals(), request)


@require_role('admin')
def app_detail(request):
    """
    App detail view
    """
    header_title, path1, path2 = u'应用详细信息', u'应用管理', u'应用详情'
    app_id = request.GET.get('id', '')
    app = get_object(App, id=app_id)
    perm_info = get_group_asset_perm(app)
    log = Log.objects.filter(host=app.name)
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'rule':
                user_group_perm = value
    print perm_info

    app_record = AppRecord.objects.filter(app=app).order_by('-alert_time')

    return my_render('upapp/app_detail.html', locals(), request)


@require_role('admin')
def app_update(request):
    """
    App update host info via ansible view
    """
    app_id = request.GET.get('id', '')
    app = get_object(App, id=app_id)
    name = request.user.username
    if not app:
        return HttpResponseRedirect(reverse('app_detail')+'?id=%s' % app_id)
    else:
        pass
    return HttpResponseRedirect(reverse('app_detail')+'?id=%s' % app_id)


@require_role('admin')
def app_update_batch(request):
    if request.method == 'POST':
        arg = request.GET.get('arg', '')
        name = unicode(request.user.username) + ' - ' + u'自动更新'
        if arg == 'all':
            app_list = App.objects.all()
        else:
            app_list = []
            app_id_all = unicode(request.POST.get('app_id_all', ''))
            app_id_all = app_id_all.split(',')
            for app_id in app_id_all:
                app = get_object(App, id=app_id)
                if app:
                    app_list.append(app)
        return HttpResponse(u'批量更新成功!')
    return HttpResponse(u'批量更新成功!')


@require_role('admin')
def app_upload(request):
    """
    Upload app excel file view
    """
    if request.method == 'POST':
        excel_file = request.FILES.get('file_name', '')
        ret = excel_to_db(excel_file)
        if ret:
            smg = u'批量添加成功'
        else:
            emg = u'批量添加失败,请检查格式.'
    return my_render('upapp/app_add_batch.html', locals(), request)

@require_role('admin')
def map_add(request):
    """
    Map add view
    添加映射
    """
    header_title, path1, path2 = u'添加映射', u'应用管理', u'添加映射'
    app_all = App.objects.all()
    af = MapForm()
    default_setting = get_object(Setting, name='default')
    if request.method == 'POST':
        af_post = MapForm(request.POST)
        name = request.POST.get('name', '')
        node_ip = request.POST.get('node_ip', '')
        node = request.POST.get('node', '')
        path = request.POST.get('path', '')
        contextroot = request.POST.get('contextroot', '')
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if Map.objects.filter(name=str(name)):
                error = u'该映射名称 %s 已存在!' % name
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                map_save = af_post.save(commit=False)
                map_save.save()
                af_post.save_m2m()

                msg = u'应用 %s 的映射添加成功' % name
            else:
                esg = u'应用 %s 的映射添加失败' % name

    return my_render('upapp/map_add.html', locals(), request)


@require_role('admin')
def map_add_batch(request):
    header_title, path1, path2 = u'添加应用', u'应用管理', u'批量添加'
    return my_render('upapp/map_add_batch.html', locals(), request)


@require_role('admin')
def map_del(request):
    """
    del a app
    删除应用
    """
    app_id = request.GET.get('id', '')
    if app_id:
        App.objects.filter(id=app_id).delete()

    if request.method == 'POST':
        app_batch = request.GET.get('arg', '')
        app_id_all = str(request.POST.get('app_id_all', ''))

        if app_batch:
            for app_id in app_id_all.split(','):
                app = get_object(App, id=app_id)
                app.delete()

    return HttpResponse(u'删除成功')


@require_role(role='super')
def map_edit(request):
    """
    edit a app
    修改应用
    """
    header_title, path1, path2 = u'修改应用', u'应用管理', u'修改应用'

    app_id = request.GET.get('id', '')
    app = get_object(App, id=app_id)
    af = AppForm(instance=app)
    if request.method == 'POST':
        af_post = AppForm(request.POST, instance=app)
        value = request.POST.get('value', '')
        name = request.POST.get('name', '')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            app_test = get_object(App, name=name)
            if app_test and app_id != unicode(app_test.id):
                emg = u'该应用名称 %s 已存在!' % name
                raise ServerError(emg)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.is_active = True if is_active else False
                af_save.save()
                af_post.save_m2m()
                info = app_diff(af_post.__dict__.get('initial'), request.POST)
                smg = u'应用 %s 修改成功' % value
            else:
                emg = u'应用 %s 修改失败' % value
                return my_render('upapp/error.html', locals(), request)
            return HttpResponseRedirect(reverse('map_detail')+'?id=%s' % app_id)

    return my_render('upapp/app_edit.html', locals(), request)

@require_role('admin')
def map_edit_batch(request):
    af = AppForm()
    name = request.user.username
    app_group_all = AppGroup.objects.all()

    if request.method == 'POST':
        app_env = request.POST.get('app_env', '')
        group = request.POST.getlist('group', [])
        comment = request.POST.get('comment', '')
        use_default_auth = request.POST.get('use_default_auth', '')
        app_id_all = unicode(request.GET.get('app_id_all', ''))
        app_id_all = app_id_all.split(',')
        for app_id in app_id_all:
            alert_list = []
            app = get_object(App, id=app_id)
            if app:
                if app_env:
                    if app.app_env != app_env:
                        app.app_env = app_env
                        alert_list.append([u'环境', app.app_env, app_env])

                if use_default_auth:
                    if use_default_auth == 'default':
                        app.use_default_auth = 1
                        alert_list.append([u'使用默认管理账号', app.use_default_auth, u'默认'])

                if group:
                    group_new, group_old, group_new_name, group_old_name = [], app.group.all(), [], []
                    for group_id in group:
                        g = get_object(AppGroup, id=group_id)
                        if g:
                            group_new.append(g)
                    if not set(group_new) < set(group_old):
                        group_instance = list(set(group_new) | set(group_old))
                        for g in group_instance:
                            group_new_name.append(g.name)
                        for g in group_old:
                            group_old_name.append(g.name)
                        app.group = group_instance
                        alert_list.append([u'应用组', ','.join(group_old_name), ','.join(group_new_name)])
                if comment:
                    if app.comment != comment:
                        app.comment = comment
                        alert_list.append([u'备注', app.comment, comment])
                app.save()

            if alert_list:
                recode_name = unicode(name) + ' - ' + u'批量'
                AppRecord.objects.create(app=app, username=recode_name, content=alert_list)
        return my_render('upapp/map_update_status.html', locals(), request)

    return my_render('upapp/map_edit_batch.html', locals(), request)


@require_role('admin')
def map_detail(request):
    """
    App detail view
    """
    header_title, path1, path2 = u'应用详细信息', u'应用管理', u'应用详情'
    app_id = request.GET.get('id', '')
    app = get_object(App, id=app_id)
    perm_info = get_group_asset_perm(app)
    log = Log.objects.filter(host=app.name)
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'rule':
                user_group_perm = value
    print perm_info

    app_record = AppRecord.objects.filter(app=app).order_by('-alert_time')

    return my_render('upapp/map_detail.html', locals(), request)


@require_role('admin')
def map_update(request):
    """
    App update host info via ansible view
    """
    app_id = request.GET.get('id', '')
    app = get_object(App, id=app_id)
    name = request.user.username
    if not app:
        return HttpResponseRedirect(reverse('app_detail')+'?id=%s' % app_id)
    else:
        pass
    return HttpResponseRedirect(reverse('map_detail')+'?id=%s' % app_id)


@require_role('admin')
def map_update_batch(request):
    if request.method == 'POST':
        arg = request.GET.get('arg', '')
        name = unicode(request.user.username) + ' - ' + u'自动更新'
        if arg == 'all':
            app_list = App.objects.all()
        else:
            app_list = []
            app_id_all = unicode(request.POST.get('app_id_all', ''))
            app_id_all = app_id_all.split(',')
            for app_id in app_id_all:
                app = get_object(App, id=app_id)
                if app:
                    app_list.append(app)
        return HttpResponse(u'批量更新成功!')
    return HttpResponse(u'批量更新成功!')


@require_role('admin')
def map_upload(request):
    """
    Upload app excel file view
    """
    if request.method == 'POST':
        excel_file = request.FILES.get('file_name', '')
        ret = excel_to_db(excel_file)
        if ret:
            smg = u'批量添加成功'
        else:
            emg = u'批量添加失败,请检查格式.'
    return my_render('upapp/map_add_batch.html', locals(), request)


@require_role('user')
def map_list(request):
    """
    map list view
    """
    header_title, path1, path2 = u'查看映射', u'应用管理', u'查看映射'
    username = request.user.username
    user_perm = request.session['role_id']
    map_envs = ENV_ENVS
    map_env = request.GET.get('app_env', '')
    node_ip = request.GET.get('node_ip', '')
    node = request.GET.get('node', '')
    path = request.GET.get('path', '')
    contextroot = request.GET.get('contextroot', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    map_id_all = request.GET.getlist("id", '')

    if user_perm != 0:
        map_find = Map.objects.all()
    else:
        map_id_all = []
        user = get_object(User, username=username)
        map_perm = get_group_user_perm(user) if user else {'map': ''}
        user_map_perm = map_perm['map'].keys()
        for map in user_map_perm:
            map_id_all.append(map.id)
        map_find = Map.objects.filter(pk__in=map_id_all)
        map_group_all = list(map_perm['map_group'])

    if map_env:
        map_find = map_find.filter(map_env__contains=map_env)

    if node_ip:
        map_find = map_find.filter(node_ip__contains=node_ip)

    if node:
        map_find = map_find.filter(node__contains=node)

    if path:
        map_find = map_find.filter(path__contains=path)

    if contextroot:
        map_find = map_find.filter(contextroot__contains=contextroot)

    if keyword:
        map_find = map_find.filter(
            Q(name__contains=keyword) |
            Q(comment__contains=keyword) |
            Q(group__name__contains=keyword))

    if export:
        if map_id_all:
            map_find = []
            for map_id in map_id_all:
                map = get_object(Map, id=map_id)
                if map:
                    map_find.append(map)
        s = write_excel(map_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upapp/app_excel_download.html', locals(), request)
    maps_list, p, maps, page_range, current_page, show_first, show_end = pages(map_find, request)
    if user_perm != 0:
        return my_render('upapp/map_list.html', locals(), request)
    else:
        return my_render('upapp/map_cu_list.html', locals(), request)




@require_role('user')
def web_list(request):
    """
    web list view
    """
    header_title, path1, path2 = u'查看服务', u'应用管理', u'查看服务'
    username = request.user.username
    user_perm = request.session['role_id']
    app_group_all = AppGroup.objects.all()
    app_types = APP_TYPE
    app_envs = ENV_ENVS
    app_status = APP_STATUS
    group_name = request.GET.get('group', '')
    app_type = request.GET.get('app_type', '')
    app_env = request.GET.get('app_env', '')
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    group_id = request.GET.get("group_id", '')
    app_id_all = request.GET.getlist("id", '')

    if group_id:
        group = get_object(AppGroup, id=group_id)
        if group:
            app_find = App.objects.filter(group=group)
    else:
        if user_perm != 0:
            app_find = App.objects.all()
        else:
            app_id_all = []
            user = get_object(User, username=username)
            app_perm = get_group_user_perm(user) if user else {'app': ''}
            user_app_perm = app_perm['app'].keys()
            for app in user_app_perm:
                app_id_all.append(app.id)
            app_find = App.objects.filter(pk__in=app_id_all)
            app_group_all = list(app_perm['app_group'])

    if app_env:
        app_find = app_find.filter(app_env__contains=app_env)

    if group_name:
        app_find = app_find.filter(group__name__contains=group_name)

    if app_type:
        app_find = app_find.filter(app_type__contains=app_type)

    if status:
        app_find = app_find.filter(status__contains=status)

    if keyword:
        app_find = app_find.filter(
            Q(name__contains=keyword) |
            Q(pre_value__contains=keyword) |
            Q(value__contains=keyword) |
            Q(comment__contains=keyword) |
            Q(group__name__contains=keyword))

    if export:
        if app_id_all:
            app_find = []
            for app_id in app_id_all:
                app = get_object(App, id=app_id)
                if app:
                    app_find.append(app)
        s = write_excel(app_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upapp/web_excel_download.html', locals(), request)
    apps_list, p, apps, page_range, current_page, show_first, show_end = pages(app_find, request)
    if user_perm != 0:
        return my_render('upapp/web_list.html', locals(), request)
    else:
        return my_render('upapp/web_cu_list.html', locals(), request)









@require_role('user')
def dns_list(request):
    """
    dns list view
    """
    header_title, path1, path2 = u'查看域名', u'应用管理', u'查看域名'
    username = request.user.username
    user_perm = request.session['role_id']
    app_group_all = AppGroup.objects.all()
    app_types = APP_TYPE
    app_envs = ENV_ENVS
    app_status = APP_STATUS
    group_name = request.GET.get('group', '')
    app_type = request.GET.get('app_type', '')
    app_env = request.GET.get('app_env', '')
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    group_id = request.GET.get("group_id", '')
    app_id_all = request.GET.getlist("id", '')

    if group_id:
        group = get_object(AppGroup, id=group_id)
        if group:
            app_find = App.objects.filter(group=group)
    else:
        if user_perm != 0:
            app_find = App.objects.all()
        else:
            app_id_all = []
            user = get_object(User, username=username)
            app_perm = get_group_user_perm(user) if user else {'app': ''}
            user_app_perm = app_perm['app'].keys()
            for app in user_app_perm:
                app_id_all.append(app.id)
            app_find = App.objects.filter(pk__in=app_id_all)
            app_group_all = list(app_perm['app_group'])

    if app_env:
        app_find = app_find.filter(app_env__contains=app_env)

    if group_name:
        app_find = app_find.filter(group__name__contains=group_name)

    if app_type:
        app_find = app_find.filter(app_type__contains=app_type)

    if status:
        app_find = app_find.filter(status__contains=status)

    if keyword:
        app_find = app_find.filter(
            Q(name__contains=keyword) |
            Q(pre_value__contains=keyword) |
            Q(value__contains=keyword) |
            Q(comment__contains=keyword) |
            Q(group__name__contains=keyword))

    if export:
        if app_id_all:
            app_find = []
            for app_id in app_id_all:
                app = get_object(App, id=app_id)
                if app:
                    app_find.append(app)
        s = write_excel(app_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upapp/web_excel_download.html', locals(), request)
    apps_list, p, apps, page_range, current_page, show_first, show_end = pages(app_find, request)
    if user_perm != 0:
        return my_render('upapp/dns_list.html', locals(), request)
    else:
        return my_render('upapp/dns_cu_list.html', locals(), request)
