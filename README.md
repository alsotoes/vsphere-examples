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

    **$ python getdatastoreclusters.py --hostname 10.0.1.200 --username alsotoes --password mypass**
- Execute (pretty print json output) 

    **$ python getdatastoreclusters.py --hostname 10.0.1.200 --username alsotoes --password mypass | python -m json.tool**
