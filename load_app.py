# -*- coding: utf-8 -*-
__author__ = 'iist'

import xml.etree.ElementTree as ET
from graph import GraphOperation
from pprint import pprint

############################
# Load app info and insert into neo4j
###########################

__ORIGN_XML__ = 'DEVWAS_snapshot_140304082643.xml'
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
    trnasform  {'Name': 'allowDispatchRemoteInclude', 'Value': 'AppDeploymentOption.No'}
    to dict structure {'allowDispatchRemoteInclude': 'AppDeploymentOption.No'}
    '''
    return {item.attrib['Name']: item.attrib['Value']}


def load_app():
    """
    Load application definition
    """
    #load application tree
    app = load_ara_xml(__ORIGN_XML__, 'Application').next()

    #get list of AppDeploymentTask nodes
    app_node = app.iterfind('AppDeploymentTask')

    #TODO: create application node
    app_root = neo_operation.insert_node('JPetStore_war', 'Application', {})[0]

    #for each node, insert into neo4j
    for attribute_set_item in app_node:
        #construct properties dict
        item_list = attribute_set_item.iterfind('TaskData/TaskColumn')
        properties = reduce(lambda x, y: dict(x.items() + y.items()),
                            map(name_value_to_dict, item_list))

        print 'add attribute set ' + attribute_set_item.attrib['Name']
        # insert node with name, label and properties
        if properties is not None:
            attribute_set = neo_operation.insert_node(attribute_set_item.attrib['Name'], 'AttributeSet', properties)[0]
        # add rel to app root
        neo_operation.add_ref(app_root, 'has properties', attribute_set)
    return app_root


def load_deployment(app):
    """
    Draw deployment model
    """
    app_deployment_xml = load_ara_xml(__ORIGN_XML__,
                                      'Application/Deployment/ApplicationDeployment/DeploymentTargetMapping/ClusteredTarget').next()
    app_target = app_deployment_xml.attrib['name']
    app_cluster = neo_operation.find_element_by_name(app_target)
    neo_operation.add_ref(app, 'deployed to', app_cluster)


def load_cell_and_nodes():
    """
    Load all the node defined in cell
    """
    cell_xml = load_ara_xml(__ORIGN_XML__, 'Cell').next()
    print 'Add Cell : ' + cell_xml.attrib['name']
    cell = neo_operation.insert_node(cell_xml.attrib['name'], 'Cell', {})[0]

    #load nodes tree
    nodes_xml = load_ara_xml(__ORIGN_XML__, 'NodeGroup').next()
    #get list of nodes
    node_group_number = nodes_xml.iterfind('NodeGroupMember')
    for item in node_group_number:
        print 'Add Node :' + item.attrib['nodeName']
        li = neo_operation.insert_node(item.attrib['nodeName'], 'Node', {})[0]
        neo_operation.add_ref(cell, 'HAS', li)


def load_servers():
    """
    Load all server defined in cell
    """
    servers_xml = load_ara_xml(__ORIGN_XML__, 'CoreGroup').next()
    server_number = servers_xml.iterfind('CoreGroupServer')

    for item in server_number:
        server_name = item.attrib['serverName']
        print 'Add Server : ' + server_name
        server = neo_operation.insert_node(server_name, 'Server', {})[0]
        li = neo_operation.find_element_by_name(item.attrib['nodeName'])
        neo_operation.add_ref(li, 'has', server)


def load_cluster():
    """
    Load cluster definition, and build relationship between cluster and node numbers
    """
    for cluster_xml in load_ara_xml(__ORIGN_XML__, 'ServerCluster'):
        cluster_numbers = cluster_xml.iterfind('ClusterMember')
        #create cluster node
        cluster_name = cluster_xml.attrib['name']
        print 'Create Cluster : ' + cluster_name
        cluster = neo_operation.insert_node(cluster_xml.attrib['name'], 'Cluster', {})[0]
        for item in cluster_numbers:
            print 'Load Cluster Number ' + item.attrib['memberName'] + ' for Cluster ' + cluster_name
            li = neo_operation.find_element_by_name(item.attrib['memberName'])
            neo_operation.add_ref(li, 'number of', cluster)


if __name__ == '__main__':
    #clean up all the notes in db
    neo_operation = GraphOperation()
    neo_operation.clean_up()

    #load asset
    load_cell_and_nodes()
    load_servers()
    load_cluster()
    app = load_app()
    load_deployment(app)


