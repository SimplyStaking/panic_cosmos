import logging
import unittest
from unittest.mock import patch

from src.monitoring.monitor_utils.get_json import get_json, get_cosmos_json

GET_JSON_FUNCTION = 'src.monitoring.monitor_utils.get_json.get_json'
GET_FUNCTION = 'src.monitoring.monitor_utils.get_json.requests.get'
LOGGER = logging.getLogger('dummy')

ENDPOINT = 'the_endpoint'
RESULT = 'the_result'


class TestGetJson(unittest.TestCase):
    class DummyGetReturn:
        CONTENT_BYTES = b'{"a":"b","c":1,"2":3}'
        CONTENT_DICT = {"a": "b", "c": 1, "2": 3}

        def __init__(self) -> None:
            self.content = self.CONTENT_BYTES

        def close(self) -> None:
            # Needs to be declared since get_json calls Response.close()
            pass

    @patch(GET_FUNCTION, return_value=DummyGetReturn())
    def test_get_json_accesses_content_and_parses_bytes_to_dict(self, _):
        self.assertEqual(TestGetJson.DummyGetReturn.CONTENT_DICT,
                         get_json(ENDPOINT, LOGGER))

    @patch(GET_FUNCTION, return_value=DummyGetReturn())
    def test_get_json_with_no_params_works_just_the_same(self, _):
        self.assertEqual(TestGetJson.DummyGetReturn.CONTENT_DICT,
                         get_json(ENDPOINT, LOGGER))


class TestGetCosmosJson(unittest.TestCase):
    @patch(GET_JSON_FUNCTION, return_value={'result': RESULT})
    def test_get_cosmos_json_returns_result_of_get_json(self, _):
        self.assertEqual(RESULT, get_cosmos_json(ENDPOINT, LOGGER))
