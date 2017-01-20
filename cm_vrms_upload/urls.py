from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect
from fileupload.views import *
from cm_vrms_wiki.views import *
from cm_vrms_baseline.views import *
from cm_vrms_upload import *
from cm_vrms_bi.views import  *
from cm_vrms_bi import *
from cm_middleware.views import *
from test_report.views import *
from cm_vrms_data import views as data_view
import os


from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
import xadmin
xadmin.autodiscover()
from xadmin.plugins import xversion
xversion.register_models()

#from xadmin.plugins import xversion
#xversion.register_models()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'upload.views.home', name='home'),

    url(r'^$', lambda x: HttpResponseRedirect('/system_detail/')),
    url(r'^upload/', include('fileupload.urls')),
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/media/','show_indexes': True }),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    
    url(r'^admin/', include(xadmin.site.urls), name='xadmin'),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^xadmin/', include(xadmin.site.urls), name='xadmin'),
    ('^hello/$', hello),
    (r'^test_form/$', test_form),
    (r'^show_form/$', show_form),
    (r'^upload_file*', upload_file),
    (r'^system_detail/$', system_detail),
    (r'^dataex_detail/$', dataex_detail),
    (r'^version_detail/$', version_detail),
    (r'^system_node_detail_*', system_node_detail),
    (r'^dataex_node_detail_*', dataex_node_detail),
    (r'^dataex_search_detail_*', dataex_search_detail),
    
    (r'^version_node_detail_*', version_node_detail),
    (r'^version_node_net_*', version_node_net),
    (r'^version_node_csv_detail_*', version_node_detail_csv),
    (r'^version_net_detail_csv_*', version_net_detail_csv),
    (r'^version_detail_for_one_system_*', version_detail_for_one_system),
    (r'^system_search_detail*', system_search_detail),
    (r'^versys_search_detail*', versys_search_detail),
    (r'^versys2_search_detail*', versys2_search_detail),
    
    (r'^wiki_index/$', wiki_index),
    (r'^wiki_index_search/$', wiki_index_search),
    (r'^application_tree_*', application_tree),
    
    
    (r'^cm_baseline*', cm_baseline),
    (r'^baseline_date_search*', baseline_date_search),
    (r'^baseline_sysver_search*', baseline_sysver_search),
    (r'^count_cm_baseline*', cm_baseline_count),
    
    (r'^login/$',  login),
    (r'^logout/$', logout),
    (r'^changepwd/$', changepwd),
    (r'^system_detail_mine/$', system_detail_mine),
    (r'^update_db_from_work/$', update_db_from_work),
    (r'^alert_info/$', alert_info),
    
    (r'^cm_bi_index*', cm_bi_index),
    (r'^bi_update*', bi_update),
    (r'^bi_problem*', bi_problem),
    (r'^bi_envi_prob*', bi_envi_prob),
    (r'^bi_human*', bi_human),
    (r'^update_db_from_work_bi/$', update_db_from_work_bi),
    
     
    (r'^get_version_info_from_work_bi/$', get_version_info_from_work_bi),
    #(r'^get_version_info_from_work_bi/$', insert_into_version),
    
    (r'^get_updatetime_from_db/$', get_updatetime_from_db),

	(r'^update_table_from_wiki/$', update_table_from_wiki),
    (r'^show_middleware/$', show_middleware),
    (r'^middleware_detail_*', middleware_detail),
    (r'^middleware_search/$', middleware_search),
    
    
    (r'^test_report_index', test_report_index),
    (r'^test_report_node_*', test_report_node),
    (r'^test_report_bar', test_report_bar),
    (r'^test_report_charts', test_report_charts),
    (r'^show_items', show_items),

    (r'^data_index/$', data_view.data_index),
    (r'^data/(?P<data_info>.+)', data_view.get_json_data),
    (r'^data_download/(?P<file_name>.+)', data_view.download_file),
    (r'^script_index/$', data_view.script_index),
    (r'^script_data/(?P<filter_info>.+)', data_view.get_json_script),
    (r'^script_download/$', data_view.script_download),
       
)


urlpatterns += patterns('',
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')}),
)


