__author__ = 'asteer'

# TODO - Add logging to debug methods rather than console output

import requests
import networkscope
import logicalswitch
import distributedrouter
import servicesrouter
import xmlformatter
import xml.dom.minidom as md
import xml.etree.ElementTree as et
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit


class Session(object):
    def __init__(self, manager, username='admin', password='default', debug=False, verify=False,
                 protocol='https', vcenterIp=None, vcenterUser='root', vcenterPass='vmware'):
        """
        Handle sessions against NSX Manager and vCenter

        :param manager: IP address of NSX Manager as string
        :param username:  Username of NSX Manager as string
        :param password:  Password of username of NSX Manager as string
        :param debug: Enable / disable debugging output as boolean
        :param verify: Enable / disable of SSL verification if https as boolean
        :param protocol: either one of http / https as string
        :param vcenterIp: vCenter IP address as string
        :param vcenterUser: Username of vCenter as string
        :param vcenterPass: Password of username of vCenter as string
        :raise Exception: If vCenter IP is configured but vCenter connection fails for some reason
        """
        self._manager = manager
        self._username = username
        self._password = password
        self._debug = debug
        self._verify = verify
        self._base = protocol + '://' + manager
        self._session = requests.Session()
        self._session.verify = self._verify
        self._session.auth = (self._username, self._password)
        self._vcenterIp = vcenterIp
        self._vcenterUser = vcenterUser
        self._vcenterPass = vcenterPass

        # if debug then enable underlying httplib debugging
        if self._debug:
            import httplib

            httplib.HTTPConnection.debuglevel = 1

        # if vCenter is in use the handle the connection
        self._si = None
        self._vcenterContent = None
        if self._vcenterIp:
            self._si = SmartConnect(host=self._vcenterIp, user=self._vcenterUser, pwd=self._vcenterPass)
            if not self._si:
                raise Exception('vCenter connection failed')
            atexit.register(Disconnect, self._si)
            self._vcenterContent = self._si.RetrieveContent()

        # Wire up the namespaces
        self.networkScope = networkscope.NetworkScope(self)
        self.logicalSwitch = logicalswitch.LogicalSwitch(self)
        self.distributedRouter = distributedrouter.DistributedRouter(self)
        self.servicesRouter = servicesrouter.ServicesRouter(self)

    def do_request(self, method, path, data=None, headers=None, params=None):
        """
        Handle API requests / responses transport

        :param method: HTTP method to use as string
        :param path: URI to append as path for API call
        :param data: Any data as PyDict (will be converted to XML string)
        :param headers: Any data as PyDict
        :return: If response is XML then an xml.etree.ElementTree else the raw content
        :raise: Any unsuccessful HTTP response code
        """
        if data:
            headers = {'Content-Type': 'application/xml'}
            data = xmlformatter.CreateXML(data.keys()[0], data[data.keys()[0]])

            if self._debug:
                print md.parseString(data).toprettyxml()

        response = self._session.request(method, self._base + path, headers=headers, params=params, data=data)
        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception("HTTP Request Failed %s" % response.content)
        
        content = response.content

        try:
            if self._debug:
                if response.headers['Content-Type'] == 'application/xml':
                    print md.parseString(content).toprettyxml()
                else:
                    print content
        except Exception as e:
            pass

        try:
            if 'Location' in response.headers:
                return self.do_request('GET', response.headers['Location'])
            elif 'content-type' in response.headers and response.headers['Content-Type'] == 'application/xml':
                return et.fromstring(content)
            else:
                return content
        except Exception as e:
            raise


    def getFromXmlString(self, xmlString, matchType, matchKey, matchValue, getKey):
        rootElement = et.fromstring(xmlString)
        return self.getFromXmlTree(rootElement, matchType, matchKey, matchValue, getKey)

    def getFromXmlTree(self, xmlTree, matchType, matchKey, matchValue, getKey):
        response = []
        rootElement = xmlTree
        for element in rootElement.iter(matchType):
            if element.find(matchKey).text == matchValue:
                response.append(element.find(getKey).text)
        return response

    def getVcenterDatacenterMoid(self, datacenterName):
        return str(self._getVcenterDatacenterFolder(datacenterName)._moId)

    def getVcenterClusterMoid(self, datacenterName, clusterName):
        for cluster in self._getVcenterDatacenterFolder(datacenterName).hostFolder.childEntity:
            if cluster.name == clusterName:
                return str(cluster._moId)

    def getVcenterDatastoreMoid(self, datacenterName, datastoreName):
        for datastore in self._getVcenterDatacenterFolder(datacenterName).datastoreFolder.childEntity:
            if datastore.name == datastoreName:
                return str(datastore._moId)

    def getVcenterNetworkMoid(self, datacenterName, networkName):
        for network in self._getVcenterDatacenterFolder(datacenterName).networkFolder.childEntity:
            if network.name == networkName:
                return str(network._moId)

    def _getVcenterDatacenterFolder(self, datacenterName):
        if self._vcenterContent == None:
            raise Exception('vCenter content not found')
        for datacenter in self._vcenterContent.rootFolder.childEntity:
            if datacenter.name == datacenterName:
                return datacenter