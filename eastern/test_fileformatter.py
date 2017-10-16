import unittest
import fileformatter
from pathlib import Path

class FileformatterTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_fileformatter_function(self):
        expected_result = (Path(__file__).parents[1] / "fixture/expect_1.yaml").read_text()
        result = fileformatter.format(Path(__file__).parents[1] / "fixture/1.yaml")
        self.assertEqual(result, expected_result)

    def test_fileformatter_function_with_env(self):
        expected_result = (Path(__file__).parents[1] / "fixture/expect_2.yaml").read_text()
        env = {
            "NAMESPACE": "beta",
            "IMAGE_TAG": "5.30.0-100"
        }
        result = fileformatter.format(Path(__file__).parents[1] / "fixture/2.yaml", env)
        self.assertEqual(result, expected_result)


    def test_fileformatter_function3(self):
        expected_result = (Path(__file__).parents[1] / "fixture/expect_3.yaml").read_text()
        env = {
            "NAMESPACE": "dev",
            "IMAGE_TAG": "5.30.0-100"
        }
        result = fileformatter.format(Path(__file__).parents[1] / "fixture/3.yaml", env)
        self.assertEqual(result, expected_result)

    def test_fileformatter_function_with_required_file_not_exist(self):
        expected_result = (Path(__file__).parents[1] / "fixture/expect_4.yaml").read_text()
        env = {
            "NAMESPACE": "unknown",
            "IMAGE_TAG": "5.30.0-100"
        }
        # result = fileformatter.format("fixture/4.yaml", env)
        # self.assertEqual(result, expected_result)
        self.assertRaises(Exception, fileformatter.format, Path(__file__).parents[1] / "fixture/4.yaml", env)
    
    def test_fileformatter_function_with_default_file(self):
        expected_result = (Path(__file__).parents[1] / "fixture/expect_5.yaml").read_text()
        env = {
            "NAMESPACE": "unknown",
            "IMAGE_TAG": "5.30.0-100"
        }
        result = fileformatter.format(Path(__file__).parents[1] / "fixture/5.yaml", env)
        self.assertEqual(result, expected_result)


    def test_fileformatter_function_with_optional_file_not_exist(self):
        expected_result = (Path(__file__).parents[1] / "fixture/expect_6.yaml").read_text()
        env = {
            "NAMESPACE": "unknown",
            "IMAGE_TAG": "5.30.0-100"
        }
        result = fileformatter.format(Path(__file__).parents[1] / "fixture/6.yaml", env)
        self.assertEqual(result, expected_result)
        # self.assertRaises(Exception, fileformatter.format, "fixture/4.yaml", env)
