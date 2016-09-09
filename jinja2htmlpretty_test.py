import unittest
from jinja2 import Environment
from jinja2htmlpretty import HTMLPretty


class TestHtmlPretty(unittest.TestCase):
    def setUp(self):
        self.env = Environment(extensions=[HTMLPretty])

    def test_around_brackets(self):

        # Arrange
        html = '''  \n\t\r  <  \n\t\r  a href="#"  \n\t\r  >  \n\t\r
         white < / br > spaces < br / > around brackets  \n\t\r
         <  \n\t\r  /  \n\t\r  a  \n\t\r  >  \n\t\r  '''
        expected = '<a href="#">white</br>spaces<br />around brackets</a>'

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_between_attributes(self):

        # Arrange
        html = '''<a  \n\t\r  href="#"  \n\t\r class="t">.</a>'''
        expected = '<a href="#" class="t">.</a>'

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_around_equal(self):
        # Arrange
        html = '''<a href  \n\t\r  = \n\t\r "#"> blah  \n\t\r =  \n\t\rblah .</a>'''
        expected = '<a href="#" class="t">.</a>'

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_final_output(self):

        # Arrange
        case = 'something wrong'
        expected = 'wrong something'
        with open('test_case.tpl', 'r') as f:
            case = f.read()
        with open('test_expected.html', 'r') as f:
            expected = f.read()

        # Act
        tpl = self.env.from_string(case)
        result = tpl.render(title='Hello tests')

        # Assert
        with open('test_result.html', 'w') as file_:
            file_.write(result)
        self._compare_html(expected, result)

    def _compare_html(self, expected, result):
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
                    expected,
                    result)
                break
        self.assertEqual('', msg, msg)


if __name__ == '__main__':
    unittest.main()
