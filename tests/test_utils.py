import unittest
from unittest.mock import patch
from utils import measure_execution_time
import logging
import time


class TestUtils(unittest.TestCase):

    @patch("logging.getLogger")
    @patch("time.time", side_effect=[0, 1])
    def test_measure_execution_time(self, time_mock, mock_logger_getter):
        @measure_execution_time
        def test_func():
            time.sleep(1)

        test_func()
        mock_logger_getter.assert_called_once()
        mock_logger_getter.return_value.info.assert_called_once_with(
            "Execution time of test_func: 1000.0000 ms"
        )
