import os
import unittest
from unittest.mock import patch, Mock, mock_open
import logging

from ..invis import UpdateIgnores, OverwriteIgnores, GitIgnoreListener

# TODO: [1] Figure out what I can test with the mocked sublime and sublime_plugin packages
