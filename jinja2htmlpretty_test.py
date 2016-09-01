import unittest
from jinja2 import Environment
from jinja2htmlpretty import HTMLPretty


class TestHtmlPretty(unittest.TestCase):

    def test_final_output(self):
        # Arrange
        env = Environment(extensions=[HTMLPretty])
        case = 'something wrong'
        expected = 'wrong something'
        with open('test_case.tpl', 'r') as f:
            case = f.read()
        with open('test_expected.html', 'r') as f:
            expected = f.read()

        # Act
        tmpl = env.from_string(case)
        result = tmpl.render(title='Hello tests')

        # Assert
        with open('test_result.html', 'w') as file_:
            file_.write(result)
        self.compare_html(expected, result)

    def compare_html(self, expected, result):
        if len(expected) <= len(result):
            length = len(expected)
        else:
            length = len(result)
        msg = ''
        for i in xrange(length):
            if expected[i] != result[i]:
                msg = "Discrepancy on char {0}:\n" \
                      "Expected:\n{1}\n" \
                      "Result:\n{2}".format(
                    i,
                    expected[:i],
                    result[:i])
                break

        self.assertEqual('', msg, msg)

if __name__ == '__main__':
    unittest.main()
