# -*- coding: utf-8 -*-
__author__ = 'iist'

import xml.etree.ElementTree as ET
from graph import GraphOperation

############################
# Load app info and insert into neo4j
###########################

__ORIGN_XML__ = 'ara.xml'


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


def insert_app_node(neo_operation, node):
    pass


def name_value_to_dict(item):
    '''
    trnasform  {'Name': 'allowDispatchRemoteInclude', 'Value': 'AppDeploymentOption.No'}
    to dict structure {'allowDispatchRemoteInclude': 'AppDeploymentOption.No'}
    '''
    item = item.attrib
    return {item['Name']: item['Value']}


def load_app():
    """
    Load application definition as following
    <Application Path="${ph:JPetStore_war_Path}" UploadApplication="true" description="" displayName="JPetStore_war">
    <AppDeploymentTask Name="AppDeploymentOptions">
      <TaskData>
        <TaskColumn Name="allowDispatchRemoteInclude" Value="AppDeploymentOption.No"/>
        <TaskColumn Name="allowServiceRemoteInclude" Value="AppDeploymentOption.No"/>
    """
    #load application tree
    app = load_ara_xml(__ORIGN_XML__, 'Application').next()

    #get list of AppDeploymentTask nodes
    app_node = app.iterfind('AppDeploymentTask')

    #create application node
    app_root = neo_operation.insert_node('JPetStore_war', 'Application', {})[0]

    #for each node, insert into neo4j
    for item in app_node:
        #construct properties dict
        properties = reduce(lambda x, y: dict(x.items() + y.items()),
                            map(name_value_to_dict, item.iterfind('TaskData/TaskColumn')))
        #get node name
        li = item.attrib
        print 'add node ' + li['Name']
        # insert node with name, label and properties
        node = neo_operation.insert_node(li['Name'], 'Application_Attribute', properties)[0]
        # add rel to app root
        neo_operation.add_ref(app_root, 'HAS', node)


def load_nodes():
    """
    Load all the node defined in cell
    """
    #load nodes tree
    nodes = load_ara_xml(__ORIGN_XML__, 'NodeGroup').next()

    #creat cell
    cell = neo_operation.insert_node('Cell', 'Cell', {})[0]

    #get list of nodes
    node_group_number = nodes.iterfind('NodeGroupMember')
    for item in node_group_number:
        li = neo_operation.insert_node(item.attrib['nodeName'], 'Node', {})[0]
        neo_operation.add_ref(cell, 'HAS', li)


def load_servers():
    """
    Load all server defined in cell
    """
    servers = load_ara_xml(__ORIGN_XML__, 'CoreGroup').next()
    server_number = servers.iterfind('CoreGroupServer')

    for item in server_number:
        print item.attrib
        server_name = item.attrib['serverName']
        server = neo_operation.insert_node(server_name, 'Server', {})[0]
        li = neo_operation.find_element_by_name(item.attrib['nodeName'])
        neo_operation.add_ref(li, 'HAS', server)


def load_cluster():
    """
    Load cluster definition, and build relationship between cluster and node numbers
    """
    cluster = load_ara_xml(__ORIGN_XML__, 'ServerCluster').next()
    cluster_numbers = cluster.iterfind('ClusterMember')
    #create cluster node
    cluster_node = neo_operation.insert_node(cluster.attrib['name'], 'Cluster', {})[0]
    for item in cluster_numbers:
        print item.attrib['memberName']
        li = neo_operation.find_element_by_name(item.attrib['memberName'])
        neo_operation.add_ref(cluster_node, 'NUMBER', li)


if __name__ == '__main__':
    #clean up all the notes in db
    neo_operation = GraphOperation()
    neo_operation.clean_up()
    load_app()
    load_nodes()
    load_servers()
    load_cluster()




