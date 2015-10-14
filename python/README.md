vsphere-examples
===========

Code using VMware vSphere API (python and perl)

* copyright:     (c) 2014 by Alvaro Soto
* license:       GPL v3, see LICENSE for more details.
* contact info:  http://headup.ws / alsotoes@gmail.com



Setting the environment
===========
- Install Virtual Environments 

    http://docs.python-guide.org/en/latest/dev/virtualenvs/
- Activate the venv

    **$ source .venv/bin/activate**
- Install the requeriments

    **$ pip install -r requirements.txt**


Running the scripts
===========
- Execute (ugly json output) 

    **$ python vmware_script.py --hostname 10.0.1.200 --username alsotoes --password mypass**
- Execute (pretty print json output) 

    **$ python vmware_script.py --hostname 10.0.1.200 --username alsotoes --password mypass | python -m json.tool**

Scripts help
===========

<pre>
$ python getdatastoreclusters.py -h
usage: getdatastoreclusters.py [-h] --hostname HOSTNAME [--port PORT]
                               --username USERNAME --password PASSWORD

Connecto to vcenter to get datastores and DS clusters.

optional arguments:
  -h, --help           show this help message and exit
  --hostname HOSTNAME  vcenter hostname or ip address
  --port PORT          port where API is running (default 443)
  --username USERNAME  Username to connect to vcenter
  --password PASSWORD  Password to connect to vcenter
</pre>

<pre>
$ python getvcenterinventory.py -h
usage: getvcenterinventory.py [-h] --hostname HOSTNAME [--port PORT]
                              --username USERNAME --password PASSWORD
                              [--instances {y,n}] [--paths {y,n}]
                              [--ips {y,n}] [--files {y,n}]

Connect to vcenter to get datastores and DS clusters.

optional arguments:
  -h, --help           show this help message and exit
  --hostname HOSTNAME  vcenter hostname or ip address
  --port PORT          port where API is running (default 443)
  --username USERNAME  Username to connect to vcenter
  --password PASSWORD  Password to connect to vcenter
  --instances {y,n}    Print instances
  --paths {y,n}        Print OS paths / partitions
  --ips {y,n}          Print ip addresses (IPv4 and IPv6)
  --files {y,n}        Print virtual machines files (logs, vmdk, etc.)
</pre>
