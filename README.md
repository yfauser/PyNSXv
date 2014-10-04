# PyNSXv Library
This is a Python Library for VMWare's NSX for vSphere Product. The aims of this project is to provide and easy to use, object based library to roll out components of NSX-v like logical switches, distributed logical routers, edge services gateway, etc.

# Getting Started
There is a seperate class file for each Subcomponent of NSX-v in `/lib/`. E.g. you will find a class to controll logical switches in `/lib/logicalswitch.py`. 
For each class we included various examples on how to use them in `/examples/`. E.g. you will find an example on how to create a new logical switch in the `/examples/LScreation.py` script.

# Class Documentation
**NOTE**: This project is still under development and currently only includes two example calls. Please check back soon as we create more classes

## Logical Switch Class `/lib/logicalswitch.py`
### Pre-requisite to do Logical Switch Operations

To work with logical switches you will first have to import the LogicalSwitch class like this:
```python
from PyNSXv.lib.logicalswitch import LogicalSwitch
```

After you imported the class you need to instanciate a new logical switch object to do further operations (call Methods) with it

```python
ls1 = LogicalSwitch(nsx_manager="192.168.178.211") 
```

The argument `nsx_manager` is the only mandatory argument. The `username` and `password` arguments have defaults set and therefore can be left out. If you have changed the password and/or username to be different from the defaults used in NSX-v, you need to supply those in the instanciation of the Logical Switch Object.

### Create a logical switch (aka. vwire or virtual wire)
Finally you can create a new logical switch using the create method of the logical switch object
```python
ls_create_result = ls1.create("TestLS")
```

The argument 'ls_name' is the only mandatory argument. There are a number of arguments that you can use that have some common defaults set

*ls_description*

usage:      set a description for the logical switch, default:    'created my PyNSXv ...'

*ls_cpmode*

usage: set the ls control plane mode, values are `UNICAST_MODE`, `MULTICAST_MODE`, `HYBRID_MODE`, default: `UNICAST_MODE`

*vdn_scope*

usage: currently always set to vdnscope-1, default: vdnscope-1

## Distributed Router Class `/lib/distribrouter.py`

### I'm still working on this one ... stay tuned!


