class TestAccessNestedMap:
    """TestAccessNestedMap class to test access_nested_map function."""

    def test_access_nested_map(self):
        '''Test that the method returns the expected results.'''
        from utils import access_nested_map
        test_cases = [
            {nested_map: {'a': 1}, path: ('a',), expected: 1},
            {nested_map: {'a': {'b': 2}}, path: ('a',), expected: {'b': 2}},
            {nested_map: {'a': {'b': 2}}, path: ('a', 'b'), expected: 2}
        ]
        for case in test_cases:
            result = access_nested_map(case['nested_map'], case['path'])
            assert result == case['expected']