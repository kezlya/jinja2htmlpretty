import unittest
from jinja2 import Environment
from jinja2htmlpretty import HTMLPretty


class TestHtmlPretty(unittest.TestCase):

    def test_final_output(self):
        # Arrange
        env = Environment(extensions=[HTMLPretty])
        case = 'something wrong'
        expected = 'wrong something'
        with open('test_case1.html', 'r') as f:
            case = f.read()
        with open('test_assert1.html', 'r') as f:
            expected = f.read()

        # Act
        tmpl = env.from_string(case)
        result = tmpl.render(title='Hello tests',)

        # Assert
        self.compare_html(expected, result)

    def compare_html(self, expected, result):
        if len(expected) <= len(result):
            length = len(expected)
        else:
            length = len(result)
        msg = ''
        for i in xrange(length):
            if expected[i] != result[i]:
                msg = "Discrepancy on char {0}:\nExpected:\n{1}\nResult:\n{2}".format(
                    i,
                    expected[:i],
                    result[:i])
                break

        self.assertEqual('', msg, msg)

if __name__ == '__main__':
    unittest.main()
