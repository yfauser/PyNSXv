__author__ = 'asteer'

import iptools
import lib.xmlformatter as xmlformatter

class UtilBase(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
                setattr(self, key, value)

    def etree_to_dict(self, t):
        return {t.tag : map(self.etree_to_dict, list(t)) or t.text}

class LogicalSubnet(UtilBase):
    """
    :param subnet: x.x.x.x/y.y.y.y format subnet address
    """
    def __init__(self, **kwargs):
        super(LogicalSubnet, self).__init__(**kwargs)

        if 'gatewayOffset' not in self.__dict__:
            self.gatewayOffset = 1

        if 'subnet' in self.__dict__:
            if not iptools.ipv4.validate_subnet(self.subnet):
                raise Exception('Invalid subnet: %s' % self.subnet)

    def gatewayIp(self):
        (network, netmask) = self.subnet.split('/')
        ip = iptools.ipv4.ip2network(network)
        return iptools.ipv4.long2ip( ip + self.gatewayOffset)


class LogicalSwitch(UtilBase):
    def __init__(self, **kwargs):
        super(LogicalSwitch, self).__init__(**kwargs)

    def __getattr__(self, item):
        return [x for x in self.virtualWire if item in x][0][item]

    def update(self, key, value):
        #TODO Cannot find any API documentation about modifying a logical switch!
        [x for x in self.virtualWire if key in x][0][key] = value

    def delete(self):
        self.session.logicalSwitch.delete(self.objectId)
        del self.virtualWire


class LogicalNetwork(UtilBase):
    def __init__(self, **kwargs):
        super(LogicalNetwork, self).__init__(**kwargs)

        self.logicalSubnet = LogicalSubnet(**kwargs)

    def createLogicalSwitch(self, session):
        if 'logicalSwitch' not in self.__dict__ or 'virtualWire' not in self.logicalSwitch.__dict__:
            self.xml = session.logicalSwitch.create(self.transportZone,
                                          '%s-%s' % (self.tenantId, self.name),
                                          tenantId=self.tenantId)
            self.logicalSwitch = LogicalSwitch(session=session, **self.etree_to_dict(self.xml))
        return self.logicalSwitch


class DistributedLogicalRouter(UtilBase):
    def __init__(self, **kwargs):
        super(DistributedLogicalRouter, self).__init__(**kwargs)
        logicalNetworks = []


class LogicalNetworks(UtilBase):
    """
    :param tenantId: A tenant ID
    """
    def __init__(self, tenantId, transportZone, **kwargs):
        super(LogicalNetworks, self).__init__(**kwargs)
        self.tenantId = tenantId
        self.transportZone = transportZone
        self._current = 0
        if 'logicalNetworks' not in self.__dict__:
            self.logicalNetworks = []

    def addLogicalNetwork(self, name, subnet, **kwargs):
        data = {'name': name,
                'subnet': subnet,
                'tenantId' : self.tenantId,
                'transportZone': self.transportZone}

        self.logicalNetworks.append(LogicalNetwork(**data))

    def __iter__(self):
        return self

    def next(self):
        try:
            self._current = self._current + 1
            return self.logicalNetworks[self._current - 1]
        except IndexError as e:
            self._current = 0
            raise StopIteration

