# -*- coding: utf-8 -*-
__author__ = 'iist'

import xml.etree.ElementTree as ET
from graph import GraphOperation


class CellBuilder():
    """
    Main class build object and relationship by handle BMA XML content
    """

    def __init__(self, bma_xml, uuid):
        self.node_list = []
        self.cluster_list = []
        self.server_list = []
        self.neo_operation = GraphOperation(uuid)
        self.xml = bma_xml

    def load_ara_xml(self, filename, path):
        """
        find path in xml, return list
        Parameters:
        filename : str
        path : xml xslt path
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        return root.iterfind(path)

    def name_value_to_dict(self, item):
        '''
        transform  {'Name': 'allowDispatchRemoteInclude', 'Value': 'AppDeploymentOption.No'}
        to dict structure {'allowDispatchRemoteInclude': 'AppDeploymentOption.No'}
        '''
        return {item.attrib['Name']: item.attrib['Value']}

    def load_app(self):
        """
        Load application definition and its relationship to cluster
        """
        for app_xml in self.load_ara_xml(self.xml, 'Application'):
            app_node = self.neo_operation.insert_node(app_xml.attrib['displayName'], 'Application', {})[0]
            self.load_app_deployment_property_set(app_xml, app_node)
            self.load_deployment(app_xml, app_node, self.cluster_list)

    def load_deployment(self, app_xml, app_node, cluster_list):
        """
        Load application deployment target
        """
        #TODO deploy to node or  cluster
        app_deployment_xml = app_xml.iterfind(
            'Deployment/ApplicationDeployment/DeploymentTargetMapping/ClusteredTarget').next()
        app_target = app_deployment_xml.attrib['name']
        for cluster in cluster_list:
            if app_target == cluster['name']:
                print 'Add ' + app_node['name'] + 'to cluster ' + app_target
                self.neo_operation.add_ref(app_node, 'deployed to', cluster)

    def load_app_deployment_property_set(self, app_xml, app_node):
        """
        Load application deployment properties
        """
        #get list of AppDeploymentTask nodes
        properties_xml = app_xml.iterfind('AppDeploymentTask')

        #for each property, insert into neo4j
        for attribute_set_item in properties_xml:
            #construct properties dict
            item_list = attribute_set_item.iterfind('TaskData/TaskColumn')
            properties = reduce(lambda x, y: dict(x.items() + y.items()),
                                map(self.name_value_to_dict, item_list))

            print 'add attribute set ' + attribute_set_item.attrib['Name']
            # insert node with name, label and properties
            if properties is not None:
                attribute_set = \
                self.neo_operation.insert_node(attribute_set_item.attrib['Name'], 'AttributeSet', properties)[0]
            # add rel to app root
            self.neo_operation.add_ref(app_node, 'has properties', attribute_set)

    def load_cell_nodes_and_servers(self):
        """
        Load all the node, server and cell
        """
        cell_xml = self.load_ara_xml(self.xml, 'Cell').next()
        print 'Add Cell : ' + cell_xml.attrib['name']
        cell = self.neo_operation.insert_node(cell_xml.attrib['name'], 'Cell', {})[0]

        #load nodes tree
        nodes_xml = self.load_ara_xml(self.xml, 'NodeGroup').next()
        #get list of nodes
        node_group_number = nodes_xml.iterfind('NodeGroupMember')

        for item in node_group_number:
            print 'Add Node :' + item.attrib['nodeName']
            li = self.neo_operation.insert_node(item.attrib['nodeName'], 'Node', {})[0]
            self.node_list.append(li)
            self.neo_operation.add_ref(cell, 'has', li)

        #load server and associated with node
        servers_xml = self.load_ara_xml(self.xml, 'CoreGroup').next()
        for server in servers_xml.iterfind('CoreGroupServer'):
            server_name = server.attrib['serverName']
            print 'Add Server : ' + server_name
            server_node = self.neo_operation.insert_node(server_name, 'Server', {})[0]
            self.server_list.append(server_node)
            for node_item in self.node_list:
                if node_item['name'] == server.attrib['nodeName']:
                    self.neo_operation.add_ref(node_item, 'has', server_node)

    def load_cluster(self):
        """
        Load cluster definition, and build relationship between cluster and node numbers
        """
        for cluster_xml in self.load_ara_xml(self.xml, 'ServerCluster'):
            cluster_numbers = cluster_xml.iterfind('ClusterMember')
            #create cluster node
            cluster_name = cluster_xml.attrib['name']
            print 'Create Cluster : ' + cluster_name
            cluster = self.neo_operation.insert_node(cluster_xml.attrib['name'], 'Cluster', {})[0]
            self.cluster_list.append(cluster)
            for item in cluster_numbers:
                print 'Load Cluster Number ' + item.attrib['memberName'] + ' for Cluster ' + cluster_name
                for server in self.server_list:
                    if server['name'] == item.attrib['memberName']:
                        self.neo_operation.add_ref(server, 'number of', cluster)


    def load(self):
        self.load_cell_nodes_and_servers()
        self.load_cluster()
        self.load_app()