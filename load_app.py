# -*- coding: utf-8 -*-
__author__ = 'iist'

import xml.etree.ElementTree as ET
from graph import GraphOperation

############################
# Load app info and insert into neo4j
###########################

__ORIGN_XML__ = 'ara46.xml'
__UUID__ = 'DEVWAS_snapshot_140304082643'


def load_ara_xml(filename, path):
    """
    find path in xml, return list
    Parameters:
    filename : str
    path : xml xslt path
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    return root.iterfind(path)


def name_value_to_dict(item):
    '''
    transform  {'Name': 'allowDispatchRemoteInclude', 'Value': 'AppDeploymentOption.No'}
    to dict structure {'allowDispatchRemoteInclude': 'AppDeploymentOption.No'}
    '''
    return {item.attrib['Name']: item.attrib['Value']}


def load_app(cluster_list):
    """
    Load application definition
    """
    for app_xml in load_ara_xml(__ORIGN_XML__, 'Application'):
        app_node = neo_operation.insert_node(app_xml.attrib['displayName'], 'Application', {})[0]
        load_app_deployment_property_set(app_xml, app_node)
        load_deployment(app_xml, app_node, cluster_list)


def load_deployment(app_xml, app_node, cluster_list):
    """
    Draw application deployment model
    """
    app_deployment_xml = app_xml.iterfind(
        'Deployment/ApplicationDeployment/DeploymentTargetMapping/ClusteredTarget').next()
    app_target = app_deployment_xml.attrib['name']
    for cluster in cluster_list:
        if app_target == cluster['name']:
            print 'Add ' + app_node['name'] + 'to cluster ' + app_target
            neo_operation.add_ref(app_node, 'deployed to', cluster)


def load_app_deployment_property_set(app_xml, app_node):
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
                            map(name_value_to_dict, item_list))

        print 'add attribute set ' + attribute_set_item.attrib['Name']
        # insert node with name, label and properties
        if properties is not None:
            attribute_set = neo_operation.insert_node(attribute_set_item.attrib['Name'], 'AttributeSet', properties)[0]
        # add rel to app root
        neo_operation.add_ref(app_node, 'has properties', attribute_set)


def load_cell_nodes_and_servers():
    """
    Load all the node, server and cell
    """
    cell_xml = load_ara_xml(__ORIGN_XML__, 'Cell').next()
    print 'Add Cell : ' + cell_xml.attrib['name']
    cell = neo_operation.insert_node(cell_xml.attrib['name'], 'Cell', {})[0]

    #load nodes tree
    nodes_xml = load_ara_xml(__ORIGN_XML__, 'NodeGroup').next()
    #get list of nodes
    node_group_number = nodes_xml.iterfind('NodeGroupMember')
    node_list = []
    for item in node_group_number:
        print 'Add Node :' + item.attrib['nodeName']
        li = neo_operation.insert_node(item.attrib['nodeName'], 'Node', {})[0]
        node_list.append(li)
        neo_operation.add_ref(cell, 'HAS', li)

    #load server and associated with node
    servers_xml = load_ara_xml(__ORIGN_XML__, 'CoreGroup').next()
    server_list = []
    for server in servers_xml.iterfind('CoreGroupServer'):
        server_name = server.attrib['serverName']
        print 'Add Server : ' + server_name
        server_node = neo_operation.insert_node(server_name, 'Server', {})[0]
        server_list.append(server_node)
        for node_item in node_list:
            if node_item['name'] == server.attrib['nodeName']:
                neo_operation.add_ref(node_item, 'has', server_node)
    return server_list


def load_cluster(server_list):
    """
    Load cluster definition, and build relationship between cluster and node numbers
    """
    cluster_list = []
    for cluster_xml in load_ara_xml(__ORIGN_XML__, 'ServerCluster'):
        cluster_numbers = cluster_xml.iterfind('ClusterMember')
        #create cluster node
        cluster_name = cluster_xml.attrib['name']
        print 'Create Cluster : ' + cluster_name
        cluster = neo_operation.insert_node(cluster_xml.attrib['name'], 'Cluster', {})[0]
        cluster_list.append(cluster)
        for item in cluster_numbers:
            print 'Load Cluster Number ' + item.attrib['memberName'] + ' for Cluster ' + cluster_name
            for server in server_list:
                if server['name'] == item.attrib['memberName']:
                    neo_operation.add_ref(server, 'number of', cluster)
    return cluster_list


if __name__ == '__main__':
    #clean up all the notes in db
    neo_operation = GraphOperation()
    neo_operation.clean_up()

    #load asset
    server_list = load_cell_nodes_and_servers()
    cluster_list = load_cluster(server_list)
    load_app(cluster_list)


