import test_templates
import unittest
from api_emulator.resource_manager import ResourceManager
import g

REST_BASE = '/redfish/v1'
g.rest_base = REST_BASE

class TestOFMF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global resource_manager
        global REST_BASE
        global TRAYS
        global SPEC
        resource_manager = ResourceManager(None, None, None, "Disable", None)
        g.app.testing = True
        cls.client = g.app.test_client()

    def test_create_computer_system(self):
        system_url = f"{REST_BASE}/Systems"
        response = self.client.post(system_url, json=test_templates.test_system)
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_create_chassis(self):
        chassis_url = f"{REST_BASE}/Chassis"
        response = self.client.post(chassis_url, json=test_templates.test_chassis)
        status_code = response.status_code
        self.assertEqual(status_code, 200)

if __name__ == '__main__':
    unittest.main()
#     main()