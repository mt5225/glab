# -*- coding: utf-8 -*-
__author__ = 'iist'

from graph import GraphOperation
from cellbuilder import CellBuilder

############################
# Load app info and insert into neo4j
###########################

if __name__ == '__main__':
    #clean up all the notes and relations in db
    neo_operation = GraphOperation()
    neo_operation.clean_up()

    #load asset
    cb = CellBuilder('ara46.xml', 'ABCD')
    cb.load()
