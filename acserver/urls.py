from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
import server.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'acserver.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', TemplateView.as_view(template_name="root")),
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<tool_id>\d+)/status/$', server.views.status),
#/1/card/12345678
    url(r'^(?P<tool_id>\d+)/card/(?P<card_id>[a-fA-F0-9]+)$', server.views.card),
#/1/grant-to-card/12345678/by-card/00112233445566
    url(r'^(?P<tool_id>\d+)/grant-to-card/(?P<to_cardid>[a-fA-F0-9]+)/by-card/(?P<by_cardid>[a-fA-F0-9]+)$', server.views.granttocard),
#/1/status/0/by/33333333
    url(r'^(?P<tool_id>\d+)/status/(?P<status>[01])/by/(?P<card_id>[a-fA-F0-9]+)$', server.views.settoolstatus),
#/1/tooluse/1/22222222
    url(r'^(?P<tool_id>\d+)/tooluse/(?P<status>[01])/(?P<card_id>[a-fA-F0-9]+)$', server.views.settooluse),
#/1/is_tool_in_use
    url(r'^(?P<tool_id>\d+)/is_tool_in_use$', server.views.isinuse),
#/1/tooluse/time/for/22222222/5
    url(r'^(?P<tool_id>\d+)/tooluse/time/for/(?P<card_id>[a-fA-F0-9]+)/(?P<duration>[0-9]+)$', server.views.settoolusetime),
#/api/get_tools_summary_for_user/1
    url(r'^api/get_tools_summary_for_user/(?P<user_id>[0-9]+)$', server.views.get_tools_summary_for_user),
#/api/get_tools_status
    url(r'^api/get_tools_status$', server.views.get_tools_status),
#/api/get_tool_runtime
    url(r'^api/get_tool_runtime_since/(?P<tool_id>[0-9]+)/(?P<start_time>[0-9]+)$', server.views.get_tool_runtime),
#/api/get_user_name/12345678
    url(r'^api/get_user_name/(?P<card_id>[a-fA-F0-9]+)$', server.views.get_user_name),
#/uitest_calheatmap1
    url(r'^uitest_calheatmap1$', server.views.calheatmap1),
#/ac_card_usage
    url(r'^ac_card_usage$', server.views.ac_card_usage, name='ac_card_usage'),
#/1/vend/item/12345678
    url(r'^(?P<tool_id>\d+)/vend/(?P<item_requested>[0-9]+)/(?P<card_id>[a-fA-F0-9]+)$', server.views.vend),
#/1/updatestock/12/
    url(r'^(?P<tool_id>\d+)/updatestock/(?P<item_requested>[0-9]+)/(?P<new_stock>[0-9+]+)$', server.views.updatestock),
#/1/getinfo/12/
    url(r'^(?P<tool_id>\d+)/getstockinfo$', server.views.getstockinfo),
#/1/getinfo/12/
    url(r'^(?P<tool_id>\d+)/addbalance/(?P<amount>[0-9]+)/(?P<card_id>[a-fA-F0-9]+)$', server.views.addbalance)
]
