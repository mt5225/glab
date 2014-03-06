# -*- coding: utf-8 -*-
__author__ = 'iist'

from graph import GraphOperation
from cellbuilder import CellBuilder
import uuid

############################
# Load app info and insert into neo4j
###########################

if __name__ == '__main__':
    #clean up all the notes and relations in db
    #TODO: record UID and other creation time infomation somewhere
    neo_operation = GraphOperation(uuid.uuid1())
    neo_operation.clean_up()

    #load asset
    #TODO: Meta data about the configuation
    #create J2EE config with BMA xml file, and set UUID
    for xml in ['data/DEVWAS_snapshot_140306054259.xml', 'DEVWAS_snapshot_140304082643.xml']:
        uid = 'UUID_' + uuid.uuid1().hex
        print uid
        cb = CellBuilder('data/DEVWAS_snapshot_140306054259.xml', uid)
        cb.load()
