# -- encoding=utf-8 --
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.cache import cache
from django.contrib.auth.decorators import user_passes_test
from releaseinfo import LOGIN_URL

def render_to(template):
    def renderer(function):
        #function_name = function.func_name
        def wrapper(request, *args, **kwargs):
            
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            
            tmpl = output.pop('TEMPLATE', template)
            #TODO:添加逻辑

            return render_to_response(tmpl, output, context_instance=RequestContext(request))
        
        return wrapper
    return renderer

def released(cache_key):
    def released(function):
        def wrapper(*args, **kwargs):
            cache.set(cache_key, None)
            result = function(*args, **kwargs)
            return result
        return wrapper
    return released

def release(cache_key):
    cache.set(cache_key, None)

def cached(cache_key, timeout=24 * 60 * 60 * 60):
    def cached(function):
        def wrapper(*args, **kwargs):
            refresh = False
            if kwargs.has_key('refresh'):
                refresh = kwargs['refresh']
            if not refresh:
                result = cache.get(cache_key)
            if refresh or result is None:
                result = function(*args, **kwargs)
                if result:
#                    if isinstance(result, dict):
#                        raise Exception(u'@cached decorator accept the function only 1 result returned')
#                    else:
                    cache.set(cache_key, result, timeout)
            #对于cache中已经存在的对象，可能会添加属性，这里用attrs来指出cache的对象是否已经存在该属性，若没有，则执行function
            #切记，function的返回值必须是该对象
            #attrs支持数组，及单个属性 
            if kwargs.has_key('attrs'):
                attrs = kwargs['attrs']
                existed = False
                if isinstance(attrs, (list, tuple)):
                    for attr in attrs:
                        existed = hasattr(result, attr)
                        if existed == False:
                            break
                elif isinstance(attrs, str):
                    existed = hasattr(result, attrs)
                
                if existed == False:
                    result = function(*args, **kwargs)
                    if result:
                        cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return cached

def get_cache(cache_key):
    return cache.get(cache_key)

def login_required(function=None):
    '''登录验证'''
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=LOGIN_URL
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
