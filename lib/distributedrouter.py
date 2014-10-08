__author__ = 'asteer'

import edgerouter


class DistributedRouter(edgerouter.EdgeRouter):
    def __init__(self, session):
        super(DistributedRouter, self).__init__(session)

