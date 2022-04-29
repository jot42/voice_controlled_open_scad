import VCOS
import shutil
import pytest
import unittest


class TestCommandLog(unittest.TestCase):

    def test_command_log_addition(self):
        VCOS.update_command_window(10, "TESTING")
        print()
        assert VCOS.command_log[len(VCOS.command_log) - 1] == "TESTING"

    def test_TextToInt(self):
        VCOS.text_to_int()

    def test_CommandWindow(self):


print("Running Tests")
unittest.main()
