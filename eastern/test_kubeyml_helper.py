import unittest
import exceptions
import kubeyml_helper
from pathlib2 import Path


class KubeymlHelperTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_supported_rolling_resources(self):
        resources = kubeyml_helper.get_supported_rolling_resources(
            "fixture/1.yaml")
        self.assertEqual(len(resources), 1)

        resource = resources[0]
        self.assertEqual(resource.name, "Deployment/wongnai-react")
        self.assertEqual(resource.namespace, "production")


if __name__ == '__main__':
    unittest.main()
