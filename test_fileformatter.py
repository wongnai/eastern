import unittest
import fileformatter
from pathlib2 import Path

class FileformatterTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fileformatter_function(self):
        expected_result = Path("fixture/expect_1.yaml").read_text()
        result = fileformatter.format("fixture/1.yaml")
        self.assertEqual(result, expected_result)

    def test_fileformatter_function_with_env(self):
        expected_result = Path("fixture/expect_2.yaml").read_text()
        env = {
            "NAMESPACE": "beta",
            "IMAGE_TAG": "5.30.0-100"
        }
        result = fileformatter.format("fixture/2.yaml", env)
        self.assertEqual(result, expected_result)


    def test_fileformatter_function3(self):
        expected_result = Path("fixture/expect_3.yaml").read_text()
        env = {
            "NAMESPACE": "dev",
            "IMAGE_TAG": "5.30.0-100"
        }
        result = fileformatter.format("fixture/3.yaml", env)
        self.assertEqual(result, expected_result)

    # def test_numbers_3_4(self):
    #     self.assertEqual(multiply(3,4), 12)



if __name__ == '__main__':
    unittest.main()