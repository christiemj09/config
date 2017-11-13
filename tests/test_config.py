"""
Test the config module.
"""

try:
    from json.decoder import JSONDecodeError  # Python 2 throws ValueError instead
except ImportError:
    pass

from tempfile import NamedTemporaryFile
import unittest
import sys

from config import from_config


@from_config
def add_function(x, y):
    """A simple adding function to test against."""
    return x + y


class TestConfig(unittest.TestCase):
    """Tests the config module."""

    def write(self, tmp, bytes_):
        """Write bytes to a temporary file."""
        tmp.write(bytes_)
        tmp.flush()
    
    def test_load_arguments(self):
        """Arguments are loaded correctly from a JSON config file."""
        
        @from_config
        def load_arguments(**kwargs):
            return kwargs

        with NamedTemporaryFile() as tmp:
        
            self.write(tmp, b'{"a": 1, "b": 2}')
            kwargs = load_arguments(tmp.name)
            
            self.assertEqual(kwargs['a'], 1)
            self.assertEqual(kwargs['b'], 2)
            self.assertNotIn('c', kwargs)
    
    def test_function(self):
        """A function can be run from a JSON config file."""       
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"x": 2, "y": 3}')
            self.assertEqual(add_function(tmp.name), 5)
    
    def test_class(self):
        """A normal class can be instantiated from a JSON config file."""
        class Adder(object):
    
            def __init__(self, x, y):
                self.x = x
                self.y = y
    
            def __call__(self):
                return self.x + self.y

        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"x": 2, "y": 3}')
            add = from_config(Adder)(tmp.name)
            self.assertEqual(add(), 5)
    
    def test_no_arguments(self):
        """A function with no arguments can be run from a JSON config file."""
        @from_config
        def five():
            return 5

        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{}')
            self.assertEqual(five(tmp.name), 5)

    def assert_error(self, action, Error, expected_msg):
        """Assert that an action raises the expected Error with the expected message."""
        with self.assertRaises(Error) as ctx:
            action()
        self.assertEqual(str(ctx.exception), expected_msg)

    def action_stager(self, func):
        """Stage the running of an action from an argument file."""
        def action_runner(filename):
            def action():
                func(filename)
            return action
        return action_runner

    def test_bad_file_py3(self):
        """Document running a function when the config file isn't JSON in Python 3."""
        if sys.version_info[0] != 3:
            return
        
        add = self.action_stager(add_function)
        
        # Empty file  
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'')
            msg = 'Expecting value: line 1 column 1 (char 0)'
            self.assert_error(add(tmp.name), JSONDecodeError, msg)
        
        # Nonempty text file
        with NamedTemporaryFile() as tmp:        
            self.write(tmp, b'This is well-formed text.')
            msg = 'Expecting value: line 1 column 1 (char 0)'
            self.assert_error(add(tmp.name), JSONDecodeError, msg)
        
        # Binary data
        with NamedTemporaryFile() as tmp:        
            self.write(tmp, b'\xec')
            msg = "'utf-8' codec can't decode byte 0xec in position 0: unexpected end of data"
            self.assert_error(add(tmp.name), UnicodeError, msg)

    def test_bad_file_py2(self):
        """Document running a function when the config file isn't JSON in Python 2."""
        if sys.version_info[0] != 2:
            return
        
        add = self.action_stager(add_function)
        
        # Empty file  
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'')
            msg = 'No JSON object could be decoded'
            self.assert_error(add(tmp.name), ValueError, msg)
        
        # Nonempty text file
        with NamedTemporaryFile() as tmp:        
            self.write(tmp, b'This is well-formed text.')
            msg = 'No JSON object could be decoded'
            self.assert_error(add(tmp.name), ValueError, msg)
        
        # Binary data
        with NamedTemporaryFile() as tmp:        
            self.write(tmp, b'\xec')
            msg = 'No JSON object could be decoded'
            self.assert_error(add(tmp.name), ValueError, msg)
    
    def test_typo_py3(self):
        """Document running a function when the JSON config file contains common typos in Python 3."""
        if sys.version_info[0] != 3:
            return
        
        add = self.action_stager(add_function)
        
        def test_on(tmp, expected_msg):
            self.assert_error(add(tmp.name), JSONDecodeError, expected_msg)
        
        # Missing quotes around property name
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1, b: 2}')
            msg = 'Expecting property name enclosed in double quotes: line 1 column 10 (char 9)'
            test_on(tmp, msg)
        
        # Missing comma between properties
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1 "b": 2}')
            msg = "Expecting ',' delimiter: line 1 column 9 (char 8)"
            test_on(tmp, msg)
        
        # Missing colon after property name
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1, "b" 2}')
            msg = "Expecting ':' delimiter: line 1 column 14 (char 13)"
            test_on(tmp, msg)
        
        # Missing closing brace
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1, "b": 2')
            msg = "Expecting ',' delimiter: line 1 column 16 (char 15)"
            test_on(tmp, msg)

    def test_typo_py2(self):
        """Document running a function when the JSON config file contains common typos in Python 2."""
        if sys.version_info[0] != 2:
            return
        
        add = self.action_stager(add_function)
        
        def test_on(tmp, expected_msg):
            self.assert_error(add(tmp.name), ValueError, expected_msg)
        
        # Missing quotes around property name
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1, b: 2}')
            msg = 'Expecting property name: line 1 column 10 (char 9)'
            test_on(tmp, msg)
        
        # Missing comma between properties
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1 "b": 2}')
            msg = "Expecting , delimiter: line 1 column 9 (char 8)"
            test_on(tmp, msg)
        
        # Missing colon after property name
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1, "b" 2}')
            msg = "Expecting : delimiter: line 1 column 14 (char 13)"
            test_on(tmp, msg)
        
        # Missing closing brace
        with NamedTemporaryFile() as tmp:
            self.write(tmp, b'{"a": 1, "b": 2')
            msg = "Expecting object: line 1 column 15 (char 14)"
            test_on(tmp, msg)


if __name__ == '__main__':
    unittest.main()

        
        