# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.core.paginator import Paginator
import logging
from utils.redisclient import rc
from releaseinfo import DETAIL_KEY_PREFIX, STATUS_RESULT_KEY,IP_KEY_PREFIX,MINIONS_SET_KEY, MINIONS_UP_SET_KEY, \
    MINIONS_DOWN_SET_KEY

logger = logging.getLogger('logger_agent')

@login_required
@render_to('agent/contentDiv.html')
@csrf_exempt
def agent(request):
    table_fields = [u'IP', u'minion-id', u'Agent安装版本', u'操作系统版本', u'状态最后更新时间', u'Agent状态']
    ajax_url = u'/agent/list/' 
    return locals()

@login_required
@csrf_exempt
def agent_list(request):
    '''
        get agent list.
    '''
    data = request.GET
    # logger.debug("#### start request agent status list")
    iDisplayLength = int(data.get('iDisplayLength'))
    iDisplayStart = int(data.get('iDisplayStart'))
    sEcho = int(data.get('sEcho'))
    #iColumns = int(request.GET.get('iColumns', 0))
    # sSearch = data.get('sSearch', None)
    # iSortCol_0 = int(data.get('iSortCol_0'))
    # sSortDir_0 = data.get('sSortDir_0')
    # order_list = [None, None, None, None, None, None]
    # order_item = order_list[iSortCol_0]

    agent_status = data.get('agent_status','all')
    agent_ips = data.get('agent_ips','').strip()
    result={}
    try:
        cache = rc.get(STATUS_RESULT_KEY)
        result  = json.loads(cache) if cache else {}
        if agent_status == 'up':
            agents = result.get('up')
        elif agent_status == 'down':
            agents = result.get('down')
        else:
            agents = result.get('down') + result.get('up')
        final_agents = set()
        if agent_ips:
            agent_ips = [ip.strip() for ip in agent_ips.split('\n') if ip and ip.strip()] #input ips.
            for agent_ip in agent_ips:
                key=IP_KEY_PREFIX+agent_ip
                if not rc.exists(key):
                    continue
                m_id = rc.get(key)
                if not rc.sismember(MINIONS_SET_KEY,m_id):
                    logger.debug("{0} is not in redis cache {1}".format(m_id,MINIONS_SET_KEY))
                    continue
                if agent_status == 'all' \
                        or (agent_status == 'down' and rc.sismember(MINIONS_DOWN_SET_KEY,m_id)) \
                        or (agent_status == 'up' and rc.sismember(MINIONS_UP_SET_KEY,m_id)):
                    final_agents.add(m_id)
            agents = list(final_agents)
        # agents = [agent for agent in agents if not str(agent).startswith("syndic")]
    except:
        logger.error("error get agentinfo")
        import traceback
        error = traceback.format_exc()
        logger.error(error)
        agents = []
    #第一个参数表示需要分页的对象，可为list、tuple、QuerySet，只要它有count()或者__len__()函数
    #第二个参数为每页显示记录数
    p = Paginator(agents, iDisplayLength)
    total = p.count #总数
    page_range = p.page_range #页数list
    page = p.page(page_range[iDisplayStart / iDisplayLength])
    object_list = page.object_list

    sdicts = {}
    sdicts["sEcho"] = sEcho
    sdicts["iTotalRecords"] = total
    sdicts["iTotalDisplayRecords"] = total
    sdicts["aaData"] = []
    for obj in object_list:
        status = 'down' if obj in result.get('down',{}) else 'up'
        # 字段不区分status, 缓存中有的话就都列出来.
        ip = rc.hget(DETAIL_KEY_PREFIX+obj,'ip')
        salt_version = rc.hget(DETAIL_KEY_PREFIX+obj,'salt_version')
        os_version = rc.hget(DETAIL_KEY_PREFIX+obj,'os_version')
        utime = rc.hget(DETAIL_KEY_PREFIX+obj,'ctime')
        data = [ip, obj, salt_version, os_version, utime, status]
        sdicts["aaData"].append(data)
    # logger.debug("#### end request agent status list")
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^agent/$', agent, name='agent'),
    url(r'^agent/list/$', agent_list),
)