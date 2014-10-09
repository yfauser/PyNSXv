__author__ = 'asteer'

#TODO - Incomplete superclass elements not finalised, basically its a copy of the distributed router at the mo
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
