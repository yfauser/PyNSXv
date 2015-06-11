# PyNSXv Library
This is a Python Library for VMWare's NSX for vSphere Product. The aims of this project is to provide and easy to use, object based library to roll out components of NSX-v like logical switches, distributed logical routers, edge services gateway, etc.

How to Install
==============

PyNSXv requires at least Python 2.7.6 and VMware's vCenter python library pyvmomi installed.

After having python installed on your system, install pyvmomi (more details on pyvmomi can be found at https://github.com/vmware/pyvmomi)

To install pyvmomi we need to python package manager 'pip' installed, e.g. on an Ubuntu box you can install pip the following way
```
sudo apt-get install python-pip
```
After 'pip' is installed, install pvmomi
```
sudo pip install --upgrade pyvmomi
```
Now you should have all dependencies installed to run PyNSXv. You can now clone this github repository into you python path. E.g. for Ubuntu Trusty (14.04) clone the repo into ```/usr/local/lib/python2.7/dist-packages```

Before you can clone the repo you will need to install git, if it is not already present on you system, e.g. on an Ubuntu box:

```
sudo apt-get install git
```

now clone the PyNSXv repo into the pythonpath:

```
cd /usr/local/lib/python2.7/dist-packages
sudo git clone https://github.com/yfauser/PyNSXv.git
```

Your setup should now be ready to use. Go into the ```/examples/yfauser/``` and ```/examples/asteer/``` pathes in ```/usr/local/lib/python2.7/dist-packages/PyNSXv/```. You will find example scripts that you can adapt to your needs. E.g. to create a logical switch in NSX copy the ```/examples/yfauser/logical_switch.py``` code, adapt it to your environment and run it.

```
cp /usr/local/lib/python2.7/dist-packages/PyNSXv/examples/yfauser/logical_switch.py ~/logical_switch.py
```
Edit ~/logical_switch.py according to your environment, and run the script
```
python logical_switch.py
```

**Please note**: The default /examples/yfauser/logical_switch.py will create a logical switch, and delete it right away. 

Important parameters:
=====================
In all the scripts, the session creation carries the important login informations. Those have been pre-populated with the default username/passwords. If those defaults are wrong, please enter the needed information in the session creation. Here are the parameters of the session class:
```
:param manager: IP address of NSX Manager as string
:param username:  Username of NSX Manager as string, default = 'admin'
:param password:  Password of username of NSX Manager as string, default = 'default'
:param debug: Enable / disable debugging output as boolean, default = 'False'
:param verify: Enable / disable of SSL verification if https as boolean, default = 'False'
:param protocol: either one of http / https as string, default = 'https'
:param vcenterIp: vCenter IP address as string, optional
:param vcenterUser: Username of vCenter as string, default = 'root'
:param vcenterPass: Password of username of vCenter as string, default = 'vmware'
```
So in the most simple case, when default users and paswords are used, the session can be created like this:
```s = session.Session('192.168.178.211')```, where the parameter is the NSX-Manager IP Address

If the default usernames and passwords are changed, you need to specify them, e.g.:
```s = session.Session('192.168.178.211', password='greatotherpassword', debug=True)```



**MORE DOCUMENTATION TO FOLLOW**


