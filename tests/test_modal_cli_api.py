import unittest
from unittest.mock import patch

import requests

from src.modal_cli import receive_data
from src.secret import DEFAULT_ERROR_RESPONSE

"""ChatGPT generated"""


class TestReceiveDataFunction(unittest.TestCase):

    def test_basic_usage(self):
        result = receive_data("e com as letras ABC?")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[1])  # Check if response is not empty

    def test_query_with_history(self):
        history = [
            [
                "quais as combinacoes possíveis com as letras A e B?",
                "Existem quatro combinações possíveis com as letras A e B, que são:A, B, AB e Nenhuma letra"
            ]
        ]
        result = receive_data("e com as letras ABC?", history)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[1])  # Check if response is not empty

    @patch('src.modal_cli.requests.post')
    def test_api_failure(self, mock_post):
        mock_post.side_effect = requests.RequestException
        result = receive_data("e com as letras ABC?")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], DEFAULT_ERROR_RESPONSE)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            receive_data(123)  # Passing an integer instead of a string

    def test_empty_query(self):
        result = receive_data("")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], DEFAULT_ERROR_RESPONSE)


if __name__ == '__main__':
    unittest.main()
