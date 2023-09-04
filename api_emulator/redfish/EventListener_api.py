from flask import request
from flask_restful import Resource
import api_emulator.redfish.constants as constants
import requests
import json
import g
from api_emulator.utils import create_path, create_object, patch_object,update_collections_json
import os

from api_emulator.redfish.Manager_api import ManagerCollectionAPI
from api_emulator.redfish.Fabric_api import FabricAPI
import api_emulator.redfish.AggregationSource_api as AggregationSource_api
import api_emulator.redfish.ConnectionMethod_api as ConnectionMethod_api
from api_emulator.redfish.templates import AggregationSource as AggregationSourceTemplate
from api_emulator.redfish.templates import ConnectionMethod as ConnectionMethodTemplate

from uuid import uuid4

import logging

config = {}

INTERNAL_ERROR = 500


# EventListener does not have a Collection API
def getRelativePath(resource):
    if '@odata.id' in resource:
        return os.path.relpath(resource['@odata.id'], '/redfish/v1/')

def patchResource(root,resource):
    patch_object(f"{root}/{getRelativePath(resource)}/index.json")

def getParentPath(obj_path):
    return "/".join(obj_path.split("/")[:-1])

def getAggregationSource():
    config = json.loads(request.data)
    if len(config['Events'])!=1:
        return
    event = config['Events'][0]
    resource = event['OriginOfCondition']['@odata.id']
    for agsource in AggregationSource_api.members:
        if resource in agsource['Links']['ResourcesAccessed']:
            return agsource

def createResource(redfish_obj):
    obj_path = getRelativePath(redfish_obj)
    file_path = create_path(constants.PATHS['Root'], obj_path)
    create_object(redfish_obj, [], [], file_path)

def fetchResource(obj_id, aggregation_source):

    resource_endpoint = f'{aggregation_source["HostName"]}/{obj_id}'
    logging.info(f"fetch: {resource_endpoint}")
    response = requests.get(resource_endpoint)

    if response.status_code == 200:
        redfish_obj = response.json()

        obj_path = getRelativePath(redfish_obj)
        file_path = create_path(constants.PATHS['Root'], obj_path)
        create_object(redfish_obj, [], [], file_path)
        aggregation_source["Links"]["ResourcesAccessed"].append(redfish_obj['@odata.id'])
        return redfish_obj

def handleEntryIfNotVisited(entry,visited,queue):
    if '@odata.id' in entry and entry['@odata.id'] not in visited:
        visited.append(entry['@odata.id'])
        queue.append(entry['@odata.id'])

def fetchResourceAndTree(id,aggregation_source,visited,queue,fetched):
    path_nodes = id.split("/")
    need_parent_prefetch = False
    for node_position in range(4,len(path_nodes)-1):
        redfish_path =  f'/redfish/v1/{"/".join(path_nodes[3:node_position+1])}'
        logging.info(f"Checking redfish path: {redfish_path}")
        if redfish_path not in visited:
            need_parent_prefetch= True
            logging.info(f"Inspect redfish path: {redfish_path}")
            queue.append(redfish_path)
            visited.append(redfish_path)
    if need_parent_prefetch: #requeue
        queue.append(id)
    else:
        redfish_obj = fetchResource(id,aggregation_source)
        fetched.append(id)
        return redfish_obj




def bfsInspection(node,aggregation_source):
    visited = []
    queue = []
    fetched = []
    visited.append(node['@odata.id'])
    queue.append(node['@odata.id'])

    def handleList(_list):
        for entry in _list:
            if type(entry) == list:
                handleList(entry)
            else:
                handleEntryIfNotVisited(entry,visited,queue)



    while queue:
        queue = sorted(queue)
        print(queue)
        id = queue.pop(0)
        redfish_obj = fetchResourceAndTree(id, aggregation_source,visited,queue,fetched)
        if redfish_obj is None or type(redfish_obj)!= dict:
            logging.info(f"Resource - {id} - not available")
            continue
        for key,val in redfish_obj.items():

            if key == 'Links':
                logging.info(f"!!!! Link... key: {key}, val: {val} ")
                if type(val)==dict:
                    for link,link_value in val.items():
                        if type(link_value) == list:
                            handleList(link_value)
                        else:
                            handleEntryIfNotVisited(link_value,visited,queue)

            if type(val) == list:
                handleList(val)
            if type(val) == dict:
                logging.info(f"--- Inspecting key:{key} - val: {val}")
                handleEntryIfNotVisited(val,visited,queue)
            if key != '@odata.id':
                continue
            if val not in visited:
                visited.append(val)
                queue.append(val)
    return visited

class EventProcessor(Resource):
    def __init__(self):
        logging.info('Event Listener init called')
        self.root = constants.PATHS['Root']


    def ResourceCreated(self, event):
        logging.info("New resource created")

        #TODO don't assume there is only one AggregationSource

        aggregation_source = getAggregationSource()

        hostname=aggregation_source["HostName"]

        response = requests.get(f"{hostname}/{event['OriginOfCondition']['@odata.id']}")
        if response.status_code == 200:
            redfish_obj = response.json()

            request.data = json.dumps(redfish_obj, indent=2).encode('utf-8')
            # Update ManagerCollection before fetching the resource subtree
            createResource(redfish_obj)
            bfsInspection(redfish_obj,aggregation_source)

        request.data = json.dumps(aggregation_source)
        patchResource(constants.PATHS['Root'],aggregation_source)



    def AggregationSourceDiscovered(self, event):
        ###
        # Fabric Agents are modelled as AggregationSource objects (RedFish v2023.1 at the time of writing this comment)
        # Registration will happen with the OFMF receiving a and event with MessageId: AggregationSourceDiscovered
        # The arguments of the event message are:
        #   - Arg1: "Redfish"
        #   - Arg2: "agent_ip:port"
        # I am also assuming that the agent name to be used is contained in the OriginOfCondifiton field of the event as in the below example:
        # {
        #    "OriginOfCondition: [
        #           "@odata.id" : "/redfish/v1/AggregationService/AggregationSource/AgentName"
        #    ]"
        # }
        logging.info("AggregationSourceDiscovered method called")
        #TODO: do we generate a new name?
        #connectionMethodId= event['OriginOfCondition']['@odata.id'].split("/")[-1]
        connectionMethodId= event['OriginOfCondition']['@odata.id']

        hostname = event['MessageArgs'][1]

        response = requests.get(f"{hostname}/{connectionMethodId}")
        if response.status_code != 200:
            raise Exception("Cannot find ConnectionMethod")

        ###
        connection_method = response.json()
        connection_method_name= connectionMethodId.split("/")[-1]
        connection_method_template = ConnectionMethodTemplate.get_ConnectionMethod_instance(
            {
                "ConnectionMethodId": connection_method_name,
                "rb": g.rest_base
            }
        )
        connection_method_template['ConnectionMethodType']= connection_method['ConnectionMethodType'],
        connection_method_template['ConnectionMethodVariant']=connection_method['ConnectionMethodVariant']

        request.data = json.dumps(connection_method_template)
        ConnectionMethod_api.ConnectionMethodAPI.post(self, connection_method_name)

        aggregationSourceId = str(uuid4())

        wildcards = {
            "AggregationSourceId": aggregationSourceId,
            "rb": g.rest_base
        }

        aggregation_source_template = AggregationSourceTemplate.get_AggregationSource_instance(wildcards)
        aggregation_source_template["HostName"] = f"{event['MessageArgs'][1]}"
        aggregation_source_template["Name"] = f"Agent {aggregationSourceId}"

        #fetch Fabric resources
        response = requests.get(f"{aggregation_source_template['HostName']}/redfish/v1/Fabrics")


        aggregation_source_template["Links"] = {
            "ConnectionMethod" : {
                "@odata.id": connection_method_template['@odata.id']
            },
            "ResourcesAccessed" : [member['@odata.id'] for member in response.json()['Members']]
        }
        logging.debug(f"aggregation_source_template: {aggregation_source_template}")

        # At this stage we are not taking care of authenticating with an agent
        request.data = json.dumps(aggregation_source_template)
        resp, msg = AggregationSource_api.AggregationSourceAPI.post(self, aggregationSourceId)
        if resp == 422:
            raise Exception(msg)

def handle_events(res):
    config = json.loads(request.data)
    for event in config['Events']:
        ###
        # Each MessageId identifies the name of the handler that will be used to process the event
        # For instance an event json with MessageId as following will be handled by the function ConnectionCreated
        # {
        #   ...
        #   'MessageId': 'Manager.1.0.ManagerCreated'
        #   ...
        # }
        ###
        handlerfunc = getattr(EventProcessor, event['MessageId'].split(".")[-1])
        handlerfunc(res, event)


# EventListener API
class EventListenerAPI(Resource):
    def __init__(self, **kwargs):
        logging.info('Event Listener init called')
        self.root = constants.PATHS['Root']
        self.auth = kwargs['auth']

    # HTTP GET
    def get(self):
        logging.info('Event Listener get called')
        return {}

    # HTTP POST Collection
    def post(self):
        logging.info('Event Listener post called')
        if request.data:
            config = json.loads(request.data)
            logging.info(f"Received request json: {config}")
            handle_events(self)

        return {}

    # HTTP PUT Collection
    def put(self):
        logging.info('Event Listener put called')
