import unittest
from unittest.mock import patch

from src.utils.user_input import yn_prompt

PROMPT_FUNCTION = 'src.utils.user_input.prompt'


class TestUserInput(unittest.TestCase):
    DUMMY_INPUT = 'DUMMY'

    @patch(PROMPT_FUNCTION, return_value='y')
    def test_yn_prompt_returns_true_for_lowercase_y(self, _):
        self.assertTrue(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @patch(PROMPT_FUNCTION, return_value='n')
    def test_yn_prompt_returns_false_for_lowercase_y(self, _):
        self.assertFalse(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @patch(PROMPT_FUNCTION, return_value='Y')
    def test_yn_prompt_returns_true_for_uppercase_y(self, _):
        self.assertTrue(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @patch(PROMPT_FUNCTION, return_value='N')
    def test_yn_prompt_returns_false_for_uppercase_n(self, _):
        self.assertFalse(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @patch(PROMPT_FUNCTION, side_effect=['/', '/', '/', 'Y'])
    def test_yn_prompt_keeps_looping_until_valid_input(self, _):
        self.assertTrue(
            yn_prompt(TestUserInput.DUMMY_INPUT))
