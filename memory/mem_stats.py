#import sys
#import traceback
#import os
import re

###############################################################################
# Explanation of metrics in /proc/meminfo can be found here
#
# http://www.redhat.com/advice/tips/meminfo.html
# and
# http://unixfoo.blogspot.com/2008/02/know-about-procmeminfo.html
# and
# http://www.centos.org/docs/5/html/5.2/Deployment_Guide/s2-proc-meminfo.html
###############################################################################

meminfo_file = "/proc/meminfo"


def metrics_handler(name):
    try:
        file = open(meminfo_file, 'r')

    except IOError:
        return 0

    value = 0

    ##### absolute calculus
    if name == 'ram_swap_used':
        return metrics_handler('ram_swap_total') - metrics_handler('ram_swap_free')
    if name == 'ram_used':
        # ram_used = memTotal - memFree - shared - buff-cache
        return metrics_handler('ram_total') - metrics_handler('ram_free') - metrics_handler('ram_shmem') - (metrics_handler('ram_buffers') + metrics_handler('ram_cached'))
    if name == 'ram_buff-cache':
        # ram_buff-cache =  ram_cached + ram_buffers
        return metrics_handler('ram_buffers') + metrics_handler('ram_cached')

    ##### percentage calculus
    if name == 'ram_free_percentage':
        return (float(metrics_handler('ram_free')) / float(metrics_handler('ram_total'))) * 100
    if name == 'ram_used_percentage':
        return (float(metrics_handler('ram_used')) / float(metrics_handler('ram_total'))) * 100
    if name == 'ram_swap_used_percentage':
        return (float(metrics_handler('ram_swap_used')) / float(metrics_handler('ram_swap_total'))) * 100
    if name == 'ram_swap_free_percentage':
        return (float(metrics_handler('ram_swap_free')) / float(metrics_handler('ram_swap_total'))) * 100
    if name == 'ram_buff-cache_percentage':
        return (float((metrics_handler('ram_buffers') + metrics_handler('ram_cached'))) / float(metrics_handler('ram_total'))) * 100


    for line in file:
        parts = re.split("\s+", line)
        if parts[0] == metric_map[name]['name'] + ":":
            # All of the measurements are in kbytes. We want to change them to GB
            if metric_map[name]['units'] == "GB":
                value = float(parts[1]) / float(1024*1024) # GB
            elif metric_map[name]['units'] == "%":
                value = parts[1] # percentage '%'
            else :
                value = float(parts[1]) / float(1024*1024) # GB
    return float(value)    # take 3 numbers after comma


def create_desc(skel, prop):
    d = skel.copy()
    for k, v in prop.iteritems():
        d[k] = v
    return d


def metric_init(params):
    global descriptors, metric_map, Desc_Skel

    descriptors = []

    Desc_Skel = {
        'name'        : 'XXX',
        'orig_name'   : 'XXX',
        'call_back'   : metrics_handler,
        'time_max'    : 60,
        'value_type'  : 'float',
        'format'      : '%.5f',
        'units'       : 'XXX',
        'slope'       : 'both',  # zero|positive|negative|both
        'description' : 'XXX',
        'groups'      : 'memory',
        }

    descriptors.append(create_desc(Desc_Skel, {
                "name": "ram_total",
                "orig_name": "MemTotal",
                "units": "GB",
                "description": "Total usable ram",
                }))

    descriptors.append(create_desc(Desc_Skel, {
                "name"       : "ram_free",
                "orig_name"  : "MemFree",
                "units"      : "GB",
                "description": "The amount of physical RAM left unused by the system. ",
                }))

    descriptors.append(create_desc(Desc_Skel, {
                "name": "ram_used",
                "orig_name": "NA",
                "units": "GB",
                "description": "The amount of physical RAM used by the system. ",
                }))

    descriptors.append(create_desc(Desc_Skel, {
                "name"       : "ram_swap_total",
                "orig_name"  : "SwapTotal",
                "units"      : "GB",
                "description": "Total amount of physical swap memory",
                }))

    descriptors.append(create_desc(Desc_Skel, {
                "name"       : "ram_swap_free",
                "orig_name"  : "SwapFree",
                "units"      : "GB",
                "description": "Total amount of swap memory free",
                }))

    descriptors.append(create_desc(Desc_Skel, {
                "name": "ram_swap_used",
                "orig_name": "NA",
                "units": "GB",
                "description": "Calculated metric.  SwapTotal - SwapFree",
                }))

    # buff-cache = ram_cached + ram_buffers
    descriptors.append(create_desc(Desc_Skel, {
                "name": "ram_cached",
                "orig_name": "Cached",
                "units": "GB",
                "description": "Cached Memory",
                }))
    descriptors.append(create_desc(Desc_Skel, {
                "name": "ram_buffers",
                "orig_name": "Buffers",
                "units": "GB",
                "description": "Buffers used",
                }))

    # represents 'shared' memory
    descriptors.append(create_desc(Desc_Skel, {
                "name": "ram_shmem",
                "orig_name": "Shmem",
                "units": "GB",
                "description": "Shmem",
                }))

    # ram_buff-cache =  ram_cached + ram_buffers
    descriptors.append(create_desc(Desc_Skel, {
        "name": "ram_buff-cache",
        "orig_name": "NA",
        "units": "GB",
        "description": "buff-cache memory",
    }))


    #################### percentage ########################
    descriptors.append(create_desc(Desc_Skel, {
        "name": "ram_free_percentage",
        "orig_name": "MemFree",
        "units": "%",
        "description": "The amount of physical RAM left unused by the system. ",
    }))

    descriptors.append(create_desc(Desc_Skel, {
        "name": "ram_used_percentage",
        "orig_name": "NA",
        "units": "%",
        "description": "The amount of physical RAM used by the system. ",
    }))

    descriptors.append(create_desc(Desc_Skel, {
        "name": "ram_buff-cache_percentage",
        "orig_name": "Buffers",
        "units": "%",
        "description": "Buff-cache",
    }))

    descriptors.append(create_desc(Desc_Skel, {
        "name": "ram_swap_free_percentage",
        "orig_name": "SwapFree",
        "units": "%",
        "description": "Total amount of swap memory free",
    }))

    descriptors.append(create_desc(Desc_Skel, {
        "name": "ram_swap_used_percentage",
        "orig_name": "NA",
        "units": "%",
        "description": "Calculated metric.  SwapTotal - SwapFree",
    }))

    # We need a metric_map that maps metric_name to the index in /proc/meminfo
    metric_map = {}

    for d in descriptors:
        metric_name = d['name']
        metric_map[metric_name] = {"name": d['orig_name'], "units": d['units']}

    return descriptors


def metric_cleanup():
    '''Clean up the metric module.'''
    pass


# This code is for debugging and unit testing
if __name__ == '__main__':
    metric_init({})
    for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %.3f' % (d['name'], v)