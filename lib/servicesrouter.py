__author__ = 'asteer + yfauser'

import edgerouter


class ServicesRouter(edgerouter.EdgeRouter):
    def __init__(self, session):
        super(ServicesRouter, self).__init__(session)

    def create(self, dc_name, cluster_name, ds_name, esg_name, esg_firstif_pg,
               esg_size="compact", ssh_enabled="false", cli_user="admin", cli_password="default"):
        esg_appliance = [{'applianceSize': esg_size}]
        esg_firstif_properties = [{'index': '0'},
                                  {'portgroupId': self._session.getVcenterNetworkMoid(dc_name, esg_firstif_pg)},
                                  {'isConnected': 'True'}]
        esg_vnics = [{'vnic': esg_firstif_properties}]
        cli_settings = [{'userName': cli_user},
                        {'password': cli_password},
                        {'remoteAccess': ssh_enabled}]

        data = {'edge':[]}
        data['edge'].append({'appliances': esg_appliance})
        data['edge'].append({'vnics': esg_vnics})
        data['edge'].append({'cliSettings': cli_settings})

        return super(ServicesRouter, self).create(dc_name, cluster_name, ds_name, esg_name, data)
    
    def DHCP_server(self, edge_id, static_binding_dict_list=None, ip_pools_dict_list=None):
        ''' This method configures the DHCP Server functionality on the NSX Edge Services Gateway
        edge_id: This is the edge id as returned by the create method
        static_binding_dict_list: This is a list containing dictionaries containing the static entry properties
        ip_pools_dict_list: This is a list containing dictionaries containing the IP Pool configurations
        static_binding_dict_list dictionary values:
          mac_address: Optional - This binds the IP to a specific MAC Address. 
                                 The entry can also be specified with the vmId and vnicId as found in vCenter
          vm_id: Optional - The vm must be connected to the given vNic below.
          vm_vnic_id: Optional - This is the vNic Id of the VM's interface this static DHCP entry is bound to
          hostname: Required- Hostname returned to the Host by DHCP
          ip_address: Required - The static IP Address to give to the VM
          default_gateway: Optional - If not set, this will return to the edge vnics primary IP to the client via DHCP
          domain_name: Optional - DNS Domain Name returned to the Host by DHCP
          primary_ns: Optional - if autoConfigDNS=true, the DNS primary/secondary ips will be generated from DNS service(if configured)
          secondary_ns: - Optional, see above
          lease_time: Optional - in second, default is "86400". valid leaseTime is a valid digit, or "infinite" 
          auto_config_dns: Optional - Defaults to true
        ip_pools_dict_list dictionary values:
          ip_range: required. the ipRange must belongs to one of a subnet of Edge vNics. 
                    And can NOT contain any ip that defined explicitly as vNic primary ip or secondary ip
          default_gateway: Optional - If not set, this will return to the edge vnics primary IP to the client via DHCP
          domain_name: Optional - DNS Domain Name returned to the Host by DHCP
          primary_ns: Optional - if autoConfigDNS=true, the DNS primary/secondary ips will be generated from DNS service(if configured)
          secondary_ns - Optional, see above
          lease_time: Optional - in second, default is "86400". valid leaseTime is a valid digit, or "infinite" 
          auto_config_dns: Optional - Defaults to true
        '''
        dhcp_server_config = [{'enabled': 'true'}]
        static_bindings_list=[]
        ip_pool_list=[]
        if static_binding_dict_list != None:
            property_keys = ['mac_address','vm_id','vm_vnic_id','default_gateway','domain_name','primary_ns','secondary_ns','lease_time','auto_config_dns']
            for static_binding_dict in static_binding_dict_list:
                static_binding_properties=[]
                for property_key in property_keys:
                    if (property_key) not in static_binding_dict: static_binding_dict[property_key]=None
                
                if static_binding_dict['mac_address'] != None: 
                    static_binding_properties.append({'macAddress': static_binding_dict['mac_address']})
                else:
                    if static_binding_dict['vm_id'] != None: static_binding_properties.append({'vmId': static_binding_dict['vm_id']})
                    if static_binding_dict['vm_vnic_id'] != None: static_binding_properties.append({'vnicId': static_binding_dict['vm_vnic_id']})
                
                static_binding_properties.append({'hostname': static_binding_dict['hostname']})
                static_binding_properties.append({'ipAddress': static_binding_dict['ip_address']})
                if static_binding_dict['default_gateway'] != None: static_binding_properties.append({'defaultGateway': static_binding_dict['default_gateway']})
                if static_binding_dict['domain_name'] != None: static_binding_properties.append({'domainName': static_binding_dict['domain_name']})
                if static_binding_dict['primary_ns'] != None: static_binding_properties.append({'primaryNameServer': static_binding_dict['primary_ns']})
                if static_binding_dict['secondary_ns'] != None: static_binding_properties.append({'secondaryNameServer': static_binding_dict['secondary_ns']})
                if static_binding_dict['lease_time'] != None: static_binding_properties.append({'leaseTime': static_binding_dict['lease_time']})
                if static_binding_dict['auto_config_dns'] != None: static_binding_properties.append({'autoConfigureDNS': static_binding_dict['auto_config_dns']})
            
                static_bindings_list.append({'staticBinding': static_binding_properties})
            
            dhcp_server_config.append({'staticBindings': static_bindings_list})
            
        if ip_pools_dict_list != None:
            property_keys = ['default_gateway','domain_name','primary_ns','secondary_ns','lease_time','auto_config_dns']
            for ip_pools_dict in ip_pools_dict_list:
                ip_pool_properties=[]
                for property_key in property_keys:
                    if (property_key) not in ip_pools_dict: ip_pools_dict[property_key]=None
                
                ip_pool_properties.append({'ipRange': ip_pools_dict['ip_range']})
                if ip_pools_dict['default_gateway'] != None: ip_pool_properties.append({'defaultGateway': ip_pools_dict['default_gateway']})
                if ip_pools_dict['domain_name'] != None: ip_pool_properties.append({'domainName': ip_pools_dict['domain_name']})
                if ip_pools_dict['primary_ns'] != None: ip_pool_properties.append({'primaryNameServer': ip_pools_dict['primary_ns']})
                if ip_pools_dict['secondary_ns'] != None: ip_pool_properties.append({'secondaryNameServer': ip_pools_dict['secondary_ns']})
                if ip_pools_dict['lease_time'] != None: ip_pool_properties.append({'leaseTime': ip_pools_dict['lease_time']})
                if ip_pools_dict['auto_config_dns'] != None: ip_pool_properties.append({'autoConfigureDNS': ip_pools_dict['auto_config_dns']})
                
                ip_pool_list.append({'ipPool': ip_pool_properties})
                
            dhcp_server_config.append({'ipPools': ip_pool_list})
            
            data = data = {'dhcp': dhcp_server_config}
        
        return self._request('PUT', '/api/4.0/edges/' + edge_id + '/dhcp/config', data=data)
