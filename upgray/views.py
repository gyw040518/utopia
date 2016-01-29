# coding:utf-8

from django.db.models import Q
from upgray.forms import RuleForm, SystemForm
from upgray.gray_api import *
from upperm.perm_api import get_group_asset_perm, get_group_user_perm

def rule_add(request):
    """
    Rule add view
    添加应用
    """
    header_title, path1, path2 = u'添加规则', u'灰度管理', u'添加规则'
    af = RuleForm()
    default_setting = get_object(Setting, name='default')
    if request.method == 'POST':
        af_post = RuleForm(request.POST)
        name = request.POST.get('name', '')
        shortname = request.POST.get('shortname','')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if Rule.objects.filter(name=name):
                error = u'该规则名称 %s 已存在!' % name
                raise ServerError(error)
            if Rule.objects.filter(shortname=str(shortname)):
                error = u'该规则简称称 %s 已存在!' % shortname
                raise ServerError(error)
            if len(shortname) > 6 or len(shortname) < 3:
                 error = u'该规则简称称 %s 不符合要求, 规则简称必须是3-6个字母!' % shortname
                 raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                rule_save = af_post.save(commit=False)
                rule_save.is_active = True if is_active else False
                rule_save.save()
                af_post.save_m2m()

                msg = u'规则 %s 添加成功' % name
            else:
                esg = u'规则 %s 添加失败' % name

    return my_render('upgray/rule_add.html', locals(), request)


@require_role('admin')
def rule_del(request):
    """
    del a rule
    删除应用
    """
    rule_id = request.GET.get('id', '')
    if rule_id:
        Rule.objects.filter(id=rule_id).delete()

    if request.method == 'POST':
        rule_batch = request.GET.get('arg', '')
        rule_id_all = str(request.POST.get('rule_id_all', ''))

        if rule_batch:
            for rule_id in rule_id_all.split(','):
                rule = get_object(Rule, id=rule_id)
                rule.delete()

    return HttpResponse(u'删除成功')


@require_role(role='super')
def rule_edit(request):
    """
    edit a rule
    修改应用
    """
    header_title, path1, path2 = u'修改规则', u'灰度管理', u'修改规则'

    rule_id = request.GET.get('id', '')
    rule = get_object(Rule, id=rule_id)
    af = RuleForm(instance=rule)
    if request.method == 'POST':
        af_post = RuleForm(request.POST, instance=rule)
        name = request.POST.get('name', '')
        shortname = request.POST.get('shortname','')
        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            rule_name_test = get_object(Rule, name=name)
            if rule_name_test and rule_id != unicode(rule_name_test.id):
                emg = u'该规则名称 %s 已存在!' % name
                raise ServerError(emg)
            rule_shortname_test = get_object(Rule,shortname=shortname)
            if rule_shortname_test and rule_id != unicode(rule_shortname_test.id):
                error = u'该规则简称 %s 已存在!' % shortname
                raise ServerError(error)
            if len(shortname) < 3 or len(shortname) > 6 :
                error = u'该规则简称称 %s 不符合要求, 规则简称必须是3-6个字母!' % shortname
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.is_active = True if is_active else False
                af_save.save()
                af_post.save_m2m()
                info = rule_diff(af_post.__dict__.get('initial'), request.POST)
                smg = u'规则 %s 修改成功' % name
            else:
                emg = u'规则 %s 修改失败' % name
                return my_render('upgray/error.html', locals(), request)
            return HttpResponseRedirect(reverse('rule_detail')+'?id=%s' % rule_id)

    return my_render('upgray/rule_edit.html', locals(), request)

@require_role('user')
def rule_list(request):
    """
    rule list view
    """
    header_title, path1, path2 = u'查看规则', u'灰度管理', u'查看规则'
    username = request.user.username
    user_perm = request.session['role_id']
    rule_status = RULE_STATUS
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    rule_id_all = request.GET.getlist("id", '')
    rule_find = Rule.objects.all()

    if user_perm != 0:
        rule_find = Rule.objects.all()
    else:
        rule_id_all = []
        user = get_object(User, username=username)
        rule_perm = get_group_user_perm(user) if user else {'rule': ''}
        user_rule_perm = rule_perm['rule'].keys()
        for rule in user_rule_perm:
            rule_id_all.append(rule.id)
        rule_find = Rule.objects.filter(pk__in=rule_id_all)

    if status:
        rule_find = rule_find.filter(status__contains=status)

    if keyword:
        rule_find = rule_find.filter(
            Q(name__contains=keyword) |
            Q(shortname__contains=keyword) |
            Q(content__contains=keyword) |
            Q(comment__contains=keyword))

    if export:
        if rule_id_all:
            rule_find = []
            for rule_id in rule_id_all:
                rule = get_object(Rule, id=rule_id)
                if rule:
                    rule_find.append(rule)
        s = write_rule_excel(rule_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upgray/rule_excel_download.html', locals(), request)
    rules_list, p, rules, page_range, current_page, show_first, show_end = pages(rule_find, request)
    if user_perm != 0:
        return my_render('upgray/rule_list.html', locals(), request)
    else:
        return my_render('upgray/rule_cu_list.html', locals(), request)

@require_role('admin')
def rule_detail(request):
    """
    rule detail view
    """
    header_title, path1, path2 = u'规则详细信息', u'灰度管理', u'规则详情'
    rule_id = request.GET.get('id', '')
    rule = get_object(Rule, id=rule_id)
    perm_info = get_group_asset_perm(rule)
    log = Log.objects.filter(host=rule.name)
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'role':
                user_group_perm = value
    print perm_info

    rule_record = RuleRecord.objects.filter(rule=rule).order_by('-alert_time')

    return my_render('upgray/rule_detail.html', locals(), request)


@require_role('admin')
def rule_update(request):
    """
    Rule update host info via ansible view
    """
    rule_id = request.GET.get('id', '')
    rule = get_object(Rule, id=rule_id)
    name = request.user.username
    if not rule:
        return HttpResponseRedirect(reverse('rule_detail')+'?id=%s' % rule_id)
    else:
        pass
    return HttpResponseRedirect(reverse('rule_detail')+'?id=%s' % rule_id)




@require_role('admin')
def system_add(request):
    """
    System add view
    添加参数
    """
    header_title, path1, path2 = u'添加系统', u'灰度管理', u'添加系统'
    system_rule_all = Rule.objects.all()
    rule_name = ''
    system_rule = Rule.objects.filter(name=rule_name)

    content_list = []
    for content in system_rule:
        content_list.append(content)

    old_version = content_list
    new_version = [a for a in content_list if a not in old_version]


    af = SystemForm()
    default_setting = get_object(Setting, name='default')



    if request.method == 'POST':
        af_post = SystemForm(request.POST)
        name = request.POST.get('name', '')
        rule_name = request.POST.get('rule_name','')
        old_version = request.POST.get('old_version',[])
        new_version = request.POST.get('new_version',[])
        obj_rule = get_object(Rule,name=rule_name)
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if System.objects.filter(name=name):
                error = u'该系统名称 %s 已存在!' % name
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                system_save = af_post.save(commit=False)
                system_save.save()
                af_post.save_m2m()

                msg = u'系统 %s 添加成功' % name
            else:
                esg = u'系统 %s 添加失败' % name

    return my_render('upgray/system_add.html', locals(), request)


@require_role('admin')
def system_del(request):
    """
    del a system
    删除参数
    """
    system_id = request.GET.get('id', '')
    if system_id:
        System.objects.filter(id=system_id).delete()

    if request.method == 'POST':
        system_batch = request.GET.get('arg', '')
        system_id_all = str(request.POST.get('system_id_all', ''))

        if system_batch:
            for system_id in system_id_all.split(','):
                system = get_object(System, id=system_id)
                system.delete()

    return HttpResponse(u'删除成功')


@require_role(role='super')
def system_edit(request):
    """
    edit a system
    修改系统
    """
    header_title, path1, path2 = u'修改系统', u'灰度管理', u'修改系统'

    system_id = request.GET.get('id', '')
    system = get_object(System, id=system_id)
    system_rule_all = Rule.objects.all()
    rule_name = request.GET.get("rule_name", '')

    if rule_name:
        system_find = System.objects.filter(rule_name=rule_name)

    af = SystemForm(instance=system)

    if request.method == 'POST':
        af_post = SystemForm(request.POST, instance=system)
        name = request.POST.get('name', '')
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            system_test = get_object(System, name=name)
            if system_test and system_id != unicode(system_test.id):
                emg = u'该系统名称 %s 已存在!' % name
                raise ServerError(emg)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                info = system_diff(af_post.__dict__.get('initial'), request.POST)
                smg = u'系统 %s 修改成功' % system
            else:
                emg = u'系统 %s 修改失败' % system
                return my_render('upgray/error.html', locals(), request)
            return HttpResponseRedirect(reverse('system_detail')+'?id=%s' % system_id)

    return my_render('upgray/system_edit.html', locals(), request)


@require_role('user')
def system_list(request):
    """
    system list view
    """
    header_title, path1, path2 = u'查看系统', u'灰度管理', u'查看系统'
    username = request.user.username
    user_perm = request.session['role_id']
    system_rule_all = Rule.objects.all()
    system_status = RULE_STATUS
    status = request.GET.get('status', '')
    rule_name = request.GET.get('rule_name', '')
    old_version = request.GET.get('old_version', '')
    new_version = request.GET.get('new_version', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    rule_id = request.GET.get("rule_id", '')
    system_id_all = request.GET.getlist("id", '')

    if rule_id:
        rule_name = get_object(Rule, id=rule_id)
        if rule_name:
            system_find = System.objects.filter(rule_name=rule_name)
    else:
        if user_perm != 0:
            system_find = System.objects.all()
        else:
            system_id_all = []
            user = get_object(User, username=username)
            system_perm = get_group_user_perm(user) if user else {'system': ''}
            user_system_perm = system_perm['system'].keys()
            for system in user_system_perm:
                system_id_all.append(system.id)
            system_find = System.objects.filter(pk__in=system_id_all)
            system_rule_all = list(system_perm['system_rule'])

    if rule_name:
        system_find = system_find.filter(rule_name__name__contains=rule_name)

    if status:
        system_find = system_find.filter(status__contains=status)

    if keyword:
        system_find = system_find.filter(
            Q(name__contains=keyword) |
            Q(rule_name__name__contains=keyword) |
            Q(old_version__contains=keyword) |
            Q(new_version__contains=keyword) |
            Q(comment__contains=keyword))

    if export:
        if system_id_all:
            system_find = []
            for system_id in system_id_all:
                system = get_object(System, id=system_id)
                if system:
                    system_find.append(system)
        s = write_system_excel(system_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('upgray/system_excel_download.html', locals(), request)
    systems_list, p, systems, page_range, current_page, show_first, show_end = pages(system_find, request)
    if user_perm != 0:
        return my_render('upgray/system_list.html', locals(), request)
    else:
        return my_render('upgray/system_cu_list.html', locals(), request)


@require_role('admin')
def system_detail(request):
    """
    System detail view
    """
    header_title, path1, path2 = u'系统详细信息', u'灰度管理', u'系统详情'
    system_id = request.GET.get('id', '')
    system = get_object(System, id=system_id)
    perm_info = get_group_asset_perm(system)
    log = Log.objects.filter(host=system.name)
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'role':
                user_group_perm = value
    print perm_info

    etcd_record = SystemRecord.objects.filter(system=system).order_by('-alert_time')

    return my_render('upgray/system_detail.html', locals(), request)


@require_role('admin')
def system_update(request):
    """
    System update host info via ansible view
    """
    system_id = request.GET.get('id', '')
    system = get_object(System, id=system_id)
    name = request.user.username
    if not system:
        return HttpResponseRedirect(reverse('etcd_detail')+'?id=%s' % system_id)
    else:
        pass
    return HttpResponseRedirect(reverse('system_detail')+'?id=%s' % system_id)
