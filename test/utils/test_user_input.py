import unittest.mock

from src.utils.user_input import yn_prompt


class TestUserInput(unittest.TestCase):
    DUMMY_INPUT = 'DUMMY'

    @unittest.mock.patch('src.utils.user_input.prompt', return_value='y')
    def test_yn_prompt_returns_true_for_lowercase_y(self, _):
        self.assertTrue(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @unittest.mock.patch('src.utils.user_input.prompt', return_value='n')
    def test_yn_prompt_returns_false_for_lowercase_y(self, _):
        self.assertFalse(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @unittest.mock.patch('src.utils.user_input.prompt', return_value='Y')
    def test_yn_prompt_returns_true_for_uppercase_y(self, _):
        self.assertTrue(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    @unittest.mock.patch('src.utils.user_input.prompt', return_value='N')
    def test_yn_prompt_returns_false_for_uppercase_n(self, _):
        self.assertFalse(
            yn_prompt(TestUserInput.DUMMY_INPUT))

    # @unittest.mock.patch('src.utils.user_input.prompt', return_value='/')
    # def test_yn_prompt_keeps_looping(self, _):
    #     pass
