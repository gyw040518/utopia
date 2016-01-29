from django.conf.urls import patterns, include, url


urlpatterns = patterns('utopia.views',
    url(r'^$', 'index', name='index'),
    url(r'^skin_config/$', 'skin_config', name='skin_config'),
    url(r'^login/$', 'Login', name='login'),
    url(r'^logout/$', 'Logout', name='logout'),
    url(r'^exec_cmd/$', 'exec_cmd', name='exec_cmd'),
    url(r'^file/upload/$', 'upload', name='file_upload'),
    url(r'^file/download/$', 'download', name='file_download'),
    url(r'^setting', 'setting', name='setting'),
    url(r'^terminal/$', 'web_terminal', name='terminal'),
    url(r'^upuser/', include('upuser.urls')),
    url(r'^upasset/', include('upasset.urls')),
    url(r'^uplog/', include('uplog.urls')),
    url(r'^upperm/', include('upperm.urls')),
    url(r'^upetcd/', include('upetcd.urls')),
    url(r'^upenv/', include('upenv.urls')),
    url(r'^upapp/', include('upapp.urls')),
     url(r'^upgray/', include('upgray.urls')),
)
