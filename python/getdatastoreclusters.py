#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import atexit
import json
import argparse

from pyVmomi import vmodl, vim
from pyVim import connect


def vconnect(host, port, username, password):
    try:
        service_instance = connect.SmartConnect(host=host, user=username, pwd=password, port=int(port))
        atexit.register(connect.Disconnect, service_instance)

        if not service_instance:
            raise SystemExit("Unable to connect to host with supplied info.")
            return -1

    except vmodl.MethodFault as error:
        print "{code: -1, msg: vmodl.MethodFault, %s}" % (error.msg)
        return -1
    except IOError as error:
        print "{code: -1, msg: IOError, %s}" % (error)
        return -1

    return service_instance


# http://stackoverflow.com/questions/1094841/
def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (math.ceil(num), x)
        num /= 1024.0

    return "%3.1f%s" % (math.ceil(num), 'TB')


def drs_information(ds_cluster):
    pass


def ds_cluster_information(datastore_cluster):
    ds_cluster = {}
    ds_cluster['name'] = datastore_cluster.name
    ds_cluster['moId'] = datastore_cluster._moId
    ds_cluster['overallStatus'] = datastore_cluster.overallStatus
    if isinstance(datastore_cluster.summary, vim.StoragePod.Summary):
        ds_cluster['capacity'] = sizeof_fmt(datastore_cluster.summary.capacity)
        ds_cluster['freeSpace'] = sizeof_fmt(datastore_cluster.summary.freeSpace)

    return ds_cluster


def datastore_information(datastore):
    ds = {}
    ds['name'] = datastore.name
    ds['moId'] = datastore._moId
    ds['overallStatus'] = datastore.overallStatus
    if isinstance(datastore.summary, vim.Datastore.Summary):
        ds['capacity'] = sizeof_fmt(datastore.summary.capacity)
        ds['freeSpace'] = sizeof_fmt(datastore.summary.freeSpace)
        ds['uncommitted'] = (None if None == datastore.summary.uncommitted else sizeof_fmt(datastore.summary.uncommitted))
        ds['accessible'] = datastore.summary.accessible
        ds['type'] = datastore.summary.type
        if isinstance(datastore.info, vim.host.NasDatastoreInfo):
            if isinstance(datastore.info.nas, vim.host.NasVolume):
                ds['remoteHost'] = datastore.info.nas.remoteHost
                ds['remotePath'] = datastore.info.nas.remotePath
    return ds


def get_ds_from_vcenter(content):
    try:
        # Get StoragePod and Datastore list
        obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.StoragePod, vim.Datastore], True)
        obj_list = obj_view.view
        obj_view.Destroy()

        cluster = {}
        datastores_nocluster = []
        for ds_cluster in obj_list:
            if isinstance(ds_cluster, vim.StoragePod):
                cluster[ds_cluster.name] = ds_cluster_information(ds_cluster)
                datastores_in_cluster = ds_cluster.childEntity

                datastores = []
                for datastore in datastores_in_cluster:
                    if isinstance(datastore, vim.Datastore):
                        datastores.append(datastore_information(datastore))
                cluster[ds_cluster.name]['datastores'] = datastores

            elif isinstance(ds_cluster, vim.Datastore) and not isinstance(ds_cluster.parent, vim.StoragePod):
                    datastores_nocluster.append(datastore_information(ds_cluster))

        cluster['NO_CLUSTER'] = {}
        cluster['NO_CLUSTER']['datastores'] = datastores_nocluster
        return cluster
    except vmodl.MethodFault as error:
        print "{code: -1, msg: vmodl.MethodFault, %s}" % (error.msg)
        return -1


def args_parse():
    parser = argparse.ArgumentParser(description='Connecto to vcenter to get datastores and DS clusters.')
    parser.add_argument("--hostname", type=str, required=True, help='vcenter hostname or ip address')
    parser.add_argument("--port", default="443", type=str, help='port where API is running (default 443)')
    parser.add_argument("--username", type=str, required=True, help='Username to connect to vcenter')
    parser.add_argument("--password", type=str, required=True, help='Password to connect to vcenter')

    return parser.parse_args()


def main():

    args = args_parse()

    try:
        service_instance = vconnect(args.hostname, args.port, args.username, args.password)

        if not service_instance:
            raise SystemExit("Could not connect to the specified host using specified username and password")
            return -1

        content = service_instance.RetrieveContent()
        print json.dumps(get_ds_from_vcenter(content))

    except vmodl.MethodFault as error:
        print "{code: -1, msg: vmodl.MethodFault, %s}" % (error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
