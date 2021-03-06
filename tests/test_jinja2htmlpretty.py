import unittest
import os
import sys
from jinja2 import Environment, FileSystemLoader
import nose
# Fix the path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
print base_dir
sys.path.insert(0, base_dir)

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

    def test_around_double_quotes(self):

        # Arrange
        html = '''<a href=  \n\t\r "  \n\t\r #  \n\t\r "  \n\t\r  >  \n\t\r
         "  \n\t\r blah   \n\t\r "  \n\t\r   </a>'''
        expected = '<a href="#">" blah "</a>'.format(HTMLPretty.SHIFT)

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
        expected = '<a href="#">blah = blah</a>'.format(HTMLPretty.SHIFT)

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

    def test_textarea_tag(self):

        # Arrange
        html = '''<html><textarea id="t" rows="1" cols="1"> \n  t \n  < / textarea></html>'''
        expected = '''<html>\n{0}<textarea id="t" rows="1" cols="1"> \n  t \n  </textarea>\n</html>'''.format(HTMLPretty.SHIFT)

        # Act
        tpl = self.env.from_string(html)
        result = tpl.render()

        # Assert
        self._compare_html(expected, result)

    def test_full_page(self):
        # Arrange
        tpl = self.env.get_template('test_case.tpl')
        with open('./tests/test_expected.html', 'r') as f:
            expected = f.read()

        # Act
        result = tpl.render().encode('utf8')

        # Assert
        with open('./tests/test_result.html', 'w') as file_:
            file_.write(result)
        self._compare_html(expected, result)

    def test_template(self):
        # Arrange
        tmpl_string = '''
        <html>
        {% if 1==1 %}
        <title>Hello</title>
        {% endif %}
        </html>
        '''
        tpl = self.env.from_string(tmpl_string)
        expected = '''<html>\n{0}<title>Hello</title>\n</html>'''.format(HTMLPretty.SHIFT)

        # Act
        result = tpl.render().encode('utf8')

        # Assert
        self._compare_html(expected, result)

    def test_template_var(self):
        # Arrange
        tmpl_string = '''
        <html>
        <title \n\t\r > Hello \n\t\r  {{val}} \n\t\r  World{{val2}} \n\t\r  </title>
        </html>
        '''
        tpl = self.env.from_string(tmpl_string)
        expected = '''<html>\n{0}<title>Hello Best World!</title>\n</html>'''.format(HTMLPretty.SHIFT)

        # Act
        result = tpl.render(val='Best', val2='!').encode('utf8')

        # Assert
        self._compare_html(expected, result)

    def test_template_sole_attribute(self):
        # Arrange
        tmpl_string = '''
        <html>
        <input type \n\t\r = \n\t\r "checkbox"
        {% if 1==1 %}checked{% endif %}
        />
        </html>
        '''
        tpl = self.env.from_string(tmpl_string)
        expected = '<html>\n{0}<input type="checkbox" checked />\n</html>'.format(HTMLPretty.SHIFT)

        # Act
        result = tpl.render().encode('utf8')

        # Assert
        self._compare_html(expected, result)

    def test_macros(self):
        # Arrange
        tmpl_string = '''
        {% import "macros.tpl" as macros %}
        <html>
            {{macros.add_images(['one','two','five'])}}
        </html>
        '''
        tpl = self.env.from_string(tmpl_string)
        expected = '<html>' \
                   '\n{0}<img src="one.jpg" />' \
                   '\n{0}<img src="two.jpg" />' \
                   '\n{0}<img src="five.jpg" />' \
                   '\n</html>'.format(HTMLPretty.SHIFT)

        # Act
        result = tpl.render().encode('utf8')

        # Assert
        self._compare_html(expected, result)

    def _compare_html(self, expected, result):
        if len(expected) <= len(result):
            length = len(expected)
        else:
            length = len(result)
        line_counter = 1
        msg = ''
        for i in xrange(length):
            if expected[i] == '\n':
                line_counter += 1

            if expected[i] != result[i]:
                msg = "Discrepancy on line {0}:\n" \
                      "Expected:\n{1}\n" \
                      "Result:\n{2}".format(
                    line_counter,
                    expected,
                    result)
                break
        self.assertFalse(result.strip() == '', "Result can't be empty")
        self.assertEqual('', msg, msg)


if __name__ == '__main__':
    res = nose.run(argv=[
        'test_jinja2htmlpretty.py', '-v', '--with-coverage', '--cover-erase',
        '--cover-package=jinja2htmlpretty',
        '--cover-html',
        '--cover-html-dir=./tests/coverage',
        '--logging-level=INFO'
    ])
