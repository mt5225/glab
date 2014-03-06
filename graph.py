# -*- coding: utf-8 -*-
__author__ = 'iist'

__NEO4J_URL__ = 'http://localhost:7474/db/data/'

from py2neo import neo4j, rel

######
# all operation to neo4j goes to this class
######
class GraphOperation():
    def __init__(self, uid):
        """
        get instance of neo4j
        """
        self.graph_db = neo4j.GraphDatabaseService(__NEO4J_URL__)
        self.uid = uid

    def clean_up(self):
        """
        clean up all nodes in database
        """
        query = neo4j.CypherQuery(self.graph_db, 'MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r')
        query.run()

    def insert_node(self, name, label, properties):
        """
        insert one node into neo4j, using name as index
        Parameter:
        __________
        name: node name
        labels: list string of lable
        properties: dict of properties
        """
        batch = neo4j.WriteBatch(self.graph_db)
        item = batch.create({"name": name})
        batch.add_to_index(neo4j.Node, 'ElementName', 'NAME', name, item)

        #while do insert, set UUID as label to group nodes in a simple set
        batch.set_labels(item, label, self.uid)
        properties = dict(properties.items() + {"name": name}.items())
        batch.set_properties(item, properties)
        return batch.submit()

    def add_ref(self, source, relationship, dest):
        """
        add relation for two nodes
        """
        batch = neo4j.WriteBatch(self.graph_db)
        batch.create(rel(source, relationship, dest))
        batch.submit()


    def find_elements_by_name(self, element_name):
        """
        find element list by names
        return node reference
        """
        batch = neo4j.ReadBatch(self.graph_db)
        batch.get_indexed_nodes('ElementName', 'NAME', element_name)
        return batch.submit()

