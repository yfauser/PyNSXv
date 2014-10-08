__author__ = 'asteer'

#TODO - Incomplete superclass elements not finalised, basically its a copy of the distributed router at the mo
import edgerouter


class ServicesRouter(edgerouter.EdgeRouter):
    def __init__(self, session):
        super(ServicesRouter, self).__init__(session)
