# C0103 - Invalid %s name "%s"
# C0111 - Missing docstring
# R0201 - Method could be a function
# pylint: disable=C0103, C0111, R0201


import unittest
from core.commons import run
from core.constants import TNS_PATH


class Error(unittest.TestCase):

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

    def tearDown(self):
        pass

    def test_001_error_reporting(self):
        output = run(TNS_PATH + " error-reporting")
        assert "Error reporting is" in output

    def test_002_error_reporting_enable(self):
        output = run(TNS_PATH + " error-reporting enable")
        assert "Error reporting is now enabled." in output

        output = run(TNS_PATH + " error-reporting status")
        assert "Error reporting is enabled." in output

    def test_003_error_reporting_disable(self):
        output = run(TNS_PATH + " error-reporting disable")
        assert "Error reporting is now disabled." in output

        output = run(TNS_PATH + " error-reporting status")
        assert "Error reporting is disabled." in output

    def test_401_error_reporting_with_invalid_parameter(self):
        command = TNS_PATH + " error-reporting invalidParam"
        output = run(command)
        assert "The value 'invalidParam' is not valid. " + \
            "Valid values are 'enable', 'disable' and 'status'" in output
