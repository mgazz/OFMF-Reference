import test_templates
import unittest
import json
from api_emulator.resource_manager import ResourceManager
from api_emulator.redfish.constants import PATHS

import g

REST_BASE = '/redfish/v1/'
g.rest_base = REST_BASE

class TestOFMF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global resource_manager
        global REST_BASE
        global TRAYS
        global SPEC

        PATHS['Root']= 'Resources/Sunfish'
        resource_manager = ResourceManager(None, None, None, "Disable", None)
        g.app.testing = True
        cls.client = g.app.test_client()

    def test_create_computer_system(self):
        system_url = f"{REST_BASE}Systems"
        response = self.client.post(system_url, json=test_templates.test_system)
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_create_chassis(self):
        chassis_url = f"{REST_BASE}Chassis"
        response = self.client.post(chassis_url, json=test_templates.test_chassis)
        status_code = response.status_code
        self.assertEqual(status_code, 200)
    
    def test_agent_registration(self):
        events_url = f"/EventListener"
        response = self.client.post(events_url, json=test_templates.test_aggregation_source_event)
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        
        manager_name = test_templates.test_aggregation_source_event["Events"][0]["OriginOfCondition"]["@odata.id"].split('/')[-1]
        conn_method = test_templates.test_aggregation_source_event["Events"][0]["OriginOfCondition"]
        aggr_source_url = f"{REST_BASE}AggregationService/AggregationSources"
        response = self.client.get(aggr_source_url)

        # validate the generation of a new AggregationSource related to the new Agent 
        aggr_source_collection = json.loads(response.data)
        aggr_source_found = False
        for aggr_source in aggr_source_collection['Members']:
            aggr_source_endpoint=self.client.get(aggr_source['@odata.id'])
            aggr_source_data = json.loads(aggr_source_endpoint.data)
            if conn_method == aggr_source_data['Links']['ConnectionMethod']:
                aggr_source_found=True

        self.assertTrue(aggr_source_found)

if __name__ == '__main__':
    unittest.main()
#     main()
