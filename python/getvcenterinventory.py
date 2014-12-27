#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import atexit
import json
import math
import sys
import re

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


def get_datacenters(content):
    datacenters = []
    try:
        children = content.rootFolder.childEntity
        for child in children:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                datacenters.append(datacenter)
            else:
                # other non-datacenter type object
                # not yep implemented !!!!
                continue
    except vmodl.MethodFault as error:
        print "{code: -1, msg: vmodl.MethodFault, %s}" % (error.msg)
        return -1

    return datacenters


def get_objects(vm_folder_entity, get_instances, get_instances_path, get_instances_ips, get_instances_files):
    folders = {}
    instances = []

    if isinstance(vm_folder_entity, vim.Datacenter):
        vm_folder = vm_folder_entity.vmFolder
        vm_list = vm_folder.childEntity
    elif isinstance(vm_folder_entity, vim.Folder):
        vm_list = vm_folder_entity.childEntity

    for vim_folder_vm in vm_list:
        if(isinstance(vim_folder_vm, vim.Folder)):
            folder_name = unicode(vim_folder_vm.name, 'utf-8')
            folders[folder_name] = get_objects(vim_folder_vm, get_instances, get_instances_path, get_instances_ips, get_instances_files)
            folders[folder_name]['moId'] = vim_folder_vm._moId
        else:
            if get_instances:
                instances.append(get_vminfo(vim_folder_vm, get_instances_path, get_instances_ips, get_instances_files))
            else:
                instances.append(get_vminfo(vim_folder_vm, get_instances_path, get_instances_ips, get_instances_files, True))

    return {'folders': folders, 'instances': instances}


# See: http://goo.gl/fjTEpW for all properties.
def get_vminfo(vm_entity, get_instances_path, get_instances_ips, get_instances_files, short_version=False):
    if(isinstance(vm_entity, vim.VirtualMachine)):
        vm_uuid = vm_entity.config.uuid
        vm_name = vm_entity.config.name
        vm_moId = vm_entity._moId

        if(short_version):
            return {'uuid': vm_uuid,
                    "name": vm_name,
                    "moId": vm_moId
                    }

        vm_version = vm_entity.config.version
        vm_guest_id = vm_entity.config.guestId
        vm_vcpu = vm_entity.config.hardware.numCPU
        vm_memory = vm_entity.config.hardware.memoryMB
        vm_template = vm_entity.config.template
        vm_path = vm_entity.summary.config.vmPathName
        vm_guest = vm_entity.summary.config.guestFullName
        vm_state = vm_entity.runtime.powerState
        vm_guest_state = vm_entity.guest.guestState
        vm_guest_tools_running = vm_entity.guest.toolsRunningStatus
        vm_guest_tools_status = vm_entity.guest.toolsStatus
        vm_guest_hostname = vm_entity.guest.hostName
        vm_guest_disk = get_disk_info(vm_entity.guest.disk, get_instances_path)
        vm_guest_net = get_nics_info(vm_entity.guest.net, get_instances_ips)
        vm_snapshot = False if vm_entity.snapshot is None else True
        vm_layout_file = get_files_info(vm_entity.layoutEx.file, get_instances_files)
        vm_unique_ds = unique_datastore(vm_path, vm_layout_file, get_instances_files)
        vm_cd_connected = atapi_connected(vm_entity)
    else:
        raise

    return {"uuid": vm_uuid,
            "guest": vm_guest,
            "state": vm_state,
            "guest_id": vm_guest_id,
            "path": vm_path,
            "name": vm_name,
            "moId": vm_moId,
            "hostname": vm_guest_hostname,
            "vcpus": vm_vcpu,
            "guest_state": vm_guest_state,
            "memory": vm_memory,
            "version": vm_version,
            "disks": vm_guest_disk,
            "nics": vm_guest_net,
            "vmtools_status": vm_guest_tools_status,
            "vmtools_running": vm_guest_tools_running,
            "files": vm_layout_file,
            "istemplate": vm_template,
            "hassnapshot": vm_snapshot,
            "unique_ds": vm_unique_ds,
            "cd_connected": vm_cd_connected
            }


def atapi_connected(vm_entity):
    is_connected = False
    for device in vm_entity.config.hardware.device:
        if(isinstance(device, vim.vm.device.VirtualCdrom)):
            is_connected = device.connectable.connected
            break
    return is_connected


def unique_datastore(vm_path, vm_layout_file, get_instances_files):
    unique = True
    regex = '.*\[(.*)\].*'

    try:
        datastore = re.compile(regex).match(vm_path).group(1)
        for datafile in vm_layout_file:
            if 'diskDescriptor' == datafile['type'] or 'diskExtent' == datafile['type']:
                if datastore != re.compile(regex).match(datafile['name']).group(1):
                    unique = False
                    break
            else:
                continue
    except AttributeError:
        unique = False

    return unique


def get_files_info(files_info, get_instances_files):
    files = []
    if(isinstance(files_info, list)):
        for file_info in files_info:
            if(isinstance(file_info, vim.vm.FileLayoutEx.FileInfo)):
                files.append({'name': file_info.name, 'type': file_info.type, 'size': file_info.size})
    else:
        return []

    if get_instances_files:
        return files
    else:
        return []


def get_nics_info(nics_info, get_instances_ips):
    nics = []
    if(isinstance(nics_info, list)):
        for nic_info in nics_info:
            if(isinstance(nic_info, vim.vm.GuestInfo.NicInfo)):
                ip_addresses = []
                if(hasattr(nic_info, 'ipConfig')):
                    if nic_info.connected:
                        if hasattr(nic_info.ipConfig, 'ipAddress'):
                            for ip_config in nic_info.ipConfig.ipAddress:
                                ip_addresses.append("%s/%s" % (ip_config.ipAddress, ip_config.prefixLength))
                        else:
                            ip_addresses.append('noIpAddress')
                    nics.append({'network': nic_info.network, 'mac_address': nic_info.macAddress, 'connected': nic_info.connected, 'ip_addresses': ip_addresses})
            else:
                continue
    else:
        return []

    if get_instances_ips:
        return nics
    else:
        return len(nics)


def get_disk_info(disks_info, get_instances_path):
    disks = []
    total = 0.0
    free = 0.0
    for disk_info in disks_info:
        disks.append({'disk_path': disk_info.diskPath, 'capacity': sizeof_fmt(disk_info.capacity), 'free_space': sizeof_fmt(disk_info.freeSpace)})
        total = total + disk_info.capacity
        free = free + disk_info.freeSpace

    disk_info = {'capacity': sizeof_fmt(total), 'free_space': sizeof_fmt(free)}

    if get_instances_path:
        disk_info['paths'] = disks

    return disk_info


# http://stackoverflow.com/questions/1094841/
def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (math.ceil(num), x)
        num /= 1024.0

    return "%3.1f%s" % (math.ceil(num), 'TB')


def get_datacenters_from_vcenter(content, GET_INSTANCES, GET_INSTANCES_PATHS, GET_INSTANCES_IPS, GET_INSTANCES_FILES):
    DC = []
    try:
        datacenters = get_datacenters(content)
        if not (datacenters is dict):
            for datacenter in datacenters:
                ds = {}
                ds[datacenter.name] = get_objects(datacenter, GET_INSTANCES, GET_INSTANCES_PATHS, GET_INSTANCES_IPS, GET_INSTANCES_FILES)
                print json.dumps(ds)
            return DC
        else:
            raise
    except vmodl.MethodFault as error:
        print "{code: -1, msg: vmodl.MethodFault, %s}" % (error.msg)
        return -1


def args_parse():
    parser = argparse.ArgumentParser(description='Connect to vcenter to get datastores and DS clusters.')
    parser.add_argument("--hostname", type=str, required=True, help='vcenter hostname or ip address')
    parser.add_argument("--port", default="443", type=str, help='port where API is running (default 443)')
    parser.add_argument("--username", type=str, required=True, help='Username to connect to vcenter')
    parser.add_argument("--password", type=str, required=True, help='Password to connect to vcenter')
    parser.add_argument("--instances", default="n", choices=["y", "n"], help='Print instances')
    parser.add_argument("--paths", default="n", choices=["y", "n"], help="Print OS paths / partitions")
    parser.add_argument("--ips", default="n", choices=["y", "n"], help="Print ip addresses (IPv4 and IPv6)")
    parser.add_argument("--files", default="n", choices=["y", "n"], help="Print virtual machines files (logs, vmdk, etc.)")
    args = parser.parse_args()

    args.files = (("y" == args.files) or False)
    args.ips = (("y" == args.ips) or False)
    args.paths = (("y" == args.paths) or False)
    args.instances = (("y" == args.instances) or False)

    if(not args.instances):
        args.instances = False
        args.paths = False
        args.ips = False
        args.files = False

    return args


def main():
    args = args_parse()

    datacenter_data = []
    try:
        service_instance = vconnect(args.hostname, args.port, args.username, args.password)

        if not service_instance:
            raise SystemExit("Could not connect to the specified host using specified username and password")
            return -1

        if not (service_instance is dict):
            content = service_instance.RetrieveContent()
            get_datacenters_from_vcenter(content, args.instances, args.paths, args.ips, args.files)
        else:
            raise

    except vmodl.MethodFault as error:
        print "{code: -1, msg: vmodl.MethodFault, %s}" % (error.msg)
        return -1
    except IOError as error:
        print "{code: -1, msg: IOError, %s}" % (error)
        return -1


# Start program
if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()
