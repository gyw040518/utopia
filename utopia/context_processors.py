from upuser.models import User
from upasset.models import Asset
from upetcd.models import Etcd
from upapp.models import App
from upgray.models import Rule
from utopia.api import *


def name_proc(request):
    user_id = request.user.id
    role_id = {'SU': 2, 'GA': 1, 'CU': 0}.get(request.user.role, 0)
    # role_id = 'SU'
    user_total_num = User.objects.all().count()
    user_active_num = User.objects.filter().count()
    host_total_num = Asset.objects.all().count()
    host_active_num = Asset.objects.filter(is_active=True).count()
    etcd_total_num = Etcd.objects.all().count()
    etcd_active_num = Etcd.objects.filter(is_active=True).count()
    app_total_num = App.objects.all().count()
    app_active_num = App.objects.filter(is_active=True).count()
    rule_total_num = Rule.objects.all().count()
    rule_active_num = Rule.objects.filter(is_active=True).count()
    request.session.set_expiry(3600)

    info_dic = {'session_user_id': user_id,
                'session_role_id': role_id,
                'user_total_num': user_total_num,
                'user_active_num': user_active_num,
                'host_total_num': host_total_num,
                'host_active_num': host_active_num,
                'etcd_total_num': etcd_total_num,
                'etcd_active_num': etcd_active_num,
                'app_total_num': app_total_num,
                'app_active_num': app_active_num,
                'rule_total_num': rule_total_num,
                'rule_active_num': rule_active_num,
                }

    return info_dic

