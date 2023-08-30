from flask import request
from flask_restful import Resource
import api_emulator.redfish.constants as constants
import requests
import json
import g
from api_emulator.utils import create_path, create_object, patch_object
import os

from api_emulator.redfish.Manager_api import ManagerCollectionAPI
from api_emulator.redfish.Fabric_api import FabricAPI
import api_emulator.redfish.AggregationSource_api as AggregationSource_api
from api_emulator.redfish.templates import AggregationSource as AggregationSourceTemplate

import logging

config = {}

INTERNAL_ERROR = 500


# EventListener does not have a Collection API
def getRelativePath(resource):
    if '@odata.id' in resource:
        return os.path.relpath(resource['@odata.id'], '/redfish/v1/')

def patchResource(root,resource):
    patch_object(f"{root}/{getRelativePath(resource)}/index.json")

def getAggregationSource():
    config = json.loads(request.data)
    if len(config['Events'])!=1:
        return
    event = config['Events'][0]
    resource = event['OriginOfCondition']['@odata.id']
    for agsource in AggregationSource_api.members:
        if resource in agsource['Links']['ResourcesAccessed']:
            return agsource



class EventProcessor(Resource):
    def __init__(self):
        logging.info('Event Listener init called')
        self.root = constants.PATHS['Root']

    def createResource(self,redfish_obj):
        obj_path = getRelativePath(redfish_obj)
        file_path = create_path(self.root, obj_path)
        create_object(redfish_obj, [], [], file_path)

    def fetchResource(self, obj_id, obj_root, host_url):

        resource_endpoint = f"{host_url}/{obj_id}"
        logging.info(f"fetch: {resource_endpoint}")
        response = requests.get(resource_endpoint)

        if response.status_code == 200:
            redfish_obj = response.json()

            obj_path = getRelativePath(redfish_obj)
            file_path = create_path(self.root, obj_path)
            create_object(redfish_obj, [], [], file_path)
            return redfish_obj


    def recursiveFetch(self, obj_dict, obj_root, aggregation_source):
        logging.info(f"dict: {obj_dict}, obj_root:{obj_root}")
        if obj_root is None or not obj_root or type(obj_dict) is not dict:
            return

        for key, value in obj_dict.items():
            logging.info(f"checking k:{key}, v:{value}")
            if key == 'Links':  # Do not explore Links for now
                logging.info(f"returning k:{key}, v:{value}")
                continue
            elif key == '@odata.id' and obj_root in value and obj_root != value:
                logging.info(f"fetch k:{key}, v:{value}")
                redfish_obj = EventProcessor.fetchResource(self, value, obj_root, aggregation_source["HostName"])
                if redfish_obj is not None and 'Collection' in redfish_obj['@odata.type']:
                    logging.info(f"Found collection {redfish_obj['@odata.type']}")
                    EventProcessor.recursiveFetch(self, {'Members': redfish_obj['Members']}, obj_root,aggregation_source)

                aggregation_source["Links"]["ResourcesAccessed"].append(redfish_obj['@odata.id'])

            if type(value) == dict:
                EventProcessor.recursiveFetch(self, value, obj_root, aggregation_source)
            elif type(value) == list:
                for element in value:
                    EventProcessor.recursiveFetch(self, element, obj_root, aggregation_source)

    def ManagerCreated(self, event):
        logging.info("ManagerCreated method called")
        host = event['MessageArgs'][0]
        port = event['MessageArgs'][1]
        response = requests.get(f"{host}:{port}/{event['OriginOfCondition']['@odata.id']}")
        if response.status_code == 200:
            redfish_obj = response.json()

            request.data = json.dumps(redfish_obj, indent=2).encode('utf-8')
            # Update ManagerCollection before fetching the resource subtree
            ManagerCollectionAPI.post(self)
            EventProcessor.recursiveFetch(self, redfish_obj, redfish_obj['@odata.id'], host, port)



    def ResourceCreated(self, event):
        logging.info("New resource created")

        #TODO don't assume there is only one AggregationSource

        aggregation_source = AggregationSource_api.members[0]

        aggregation_source = getAggregationSource()
        #if aggregation_source is None:
        #  return error

        hostname=aggregation_source["HostName"]

        response = requests.get(f"{hostname}/{event['OriginOfCondition']['@odata.id']}")
        if response.status_code == 200:
            redfish_obj = response.json()

            request.data = json.dumps(redfish_obj, indent=2).encode('utf-8')
            # Update ManagerCollection before fetching the resource subtree
            EventProcessor.createResource(self,redfish_obj)
            EventProcessor.recursiveFetch(self, redfish_obj, redfish_obj['@odata.id'], aggregation_source)

        request.data = json.dumps(aggregation_source)
        patchResource(self.root,aggregation_source)



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
        aggregationSourceId = event['OriginOfCondition']['@odata.id'].split("/")[-1]
        wildcards = {
            "AggregationSourceId": aggregationSourceId,
            "rb": g.rest_base
        }


        aggregation_source_template = AggregationSourceTemplate.get_AggregationSource_instance(wildcards)
        aggregation_source_template["HostName"] = f"{event['MessageArgs'][0]}:{event['MessageArgs'][1]}"
        aggregation_source_template["Name"] = f"Agent {aggregationSourceId}"
        response = requests.get(f"{aggregation_source_template['HostName']}/redfish/v1/Fabrics")

        aggregation_source_template["Links"] = {
            "ConnectionMethod" : {},
            "ResourcesAccessed" : [member['@odata.id'] for member in response.json()['Members']]
        }
        logging.debug(f"aggregation_source_template: {aggregation_source_template}")

        # At this stage we are not taking care of authenticating with an agent
        request.data = json.dumps(aggregation_source_template)
        AggregationSource_api.AggregationSourceAPI.post(self, aggregationSourceId)

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
