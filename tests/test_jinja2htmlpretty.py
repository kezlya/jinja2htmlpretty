import unittest
import os
from jinja2 import Environment, FileSystemLoader
from jinja2htmlpretty import HTMLPretty


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestHtmlPretty(unittest.TestCase):
    def setUp(self):
        self.env = Environment(loader=FileSystemLoader(THIS_DIR),
                               extensions=[HTMLPretty])

    def test_text_between_tags(self):

        # Arrange
        html = '''<html><div><p> \n\t\r white \n\t\r space \n\t\r</p></div>
         <div><p> \n\t\r around  \n\t\r brackets \n\t\r </p></div></html>\n\t\r'''
        expected = '<html>\n{0}<div>\n{0}{0}<p>white space</p>\n{0}</div>\n{0}' \
                   '<div>\n{0}{0}<p>around brackets</p>\n{0}</div>\n</html>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_around_brackets(self):

        # Arrange
        html = '''  \n\t\r  <  \n\t\r  a href="#"  \n\t\r  >  \n\t\r
         blah  <  \n\t\r  /  \n\t\r  a  \n\t\r  >  \n\t\r  '''
        expected = '<a href="#">blah</a>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_between_attributes(self):

        # Arrange
        html = '''<a  \n\t\r  href="#"  \n\t\r class="t"><img \n\t\r src="#"\n\t\r ></a>'''
        expected = '<a href="#" class="t">\n{0}<img src="#">\n</a>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_around_equal(self):

        # Arrange
        html = '''<a href  \n\t\r  = \n\t\r "#"> blah  \n\t\r =  \n\t\rblah</a>'''
        expected = '<a href="#">blah=blah</a>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_ul_li(self):

        # Arrange
        html = '''  \n\t\r  < \n\t\r ul \n\t\r >  \n\t\r
         < \n\t\r li \n\t\r >  \n\t\r  <img src="blah">  \n\t\r
         < \n\t\r / \n\t\r li \n\t\r >  \n\t\r
         < \n\t\r / \n\t\r ul \n\t\r >  \n\t\r  '''
        expected = '<ul>\n{0}<li>\n{0}{0}<img src="blah">\n{0}</li>\n</ul>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_solo_tag(self):

        # Arrange
        html = ''' <html>  \n\t\r<meta link=""/>  \n\t\r <meta link=""> \n\t\r
         \n\t\r < img src="#"/ >  \n\t\r </html>  '''
        expected = '<html>\n{0}<meta link=""/>\n{0}<meta link="">\n{0}' \
                   '<img src="#"/>\n</html>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_br_tag(self):

        # Arrange
        html = '''<html><div><p>1\n\t\r  <\n\t\r /\n\t\r br\n\t\r > \n\t\r one</p></div>
         <div><p>2  \n\t\r <\n\t\r br\n\t\r > \n\t\r  two</p></div>
         <div><p>3  \n\t\r < \n\t\r br \n\t\r / \n\t\r > \n\t\r  three</p></div></html>'''
        expected = '<html>\n{0}<div>\n{0}{0}<p>1</br>one</p>\n{0}</div>\n{0}' \
                   '<div>\n{0}{0}<p>2<br>two</p>\n{0}</div>\n{0}' \
                   '<div>\n{0}{0}<p>3<br />three</p>\n{0}</div>\n</html>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_script_tag(self):

        # Arrange
        html = '''<html><script> \n     alert("blah"); \n  </script></html>'''
        expected = '<html>\n{0}<script> \n     alert("blah"); \n  </script>\n</html>'.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)


    def test_final_output(self):
        # Arrange
        tpl = self.env.get_template('test_case.tpl')
        with open('test_expected.html', 'r') as f:
            expected = f.read()

        # Act
        result = tpl.render()

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
        self.assertFalse(result.strip() == '', "Result can't be empty")
        self.assertEqual('', msg, msg)


if __name__ == '__main__':
    unittest.main()
