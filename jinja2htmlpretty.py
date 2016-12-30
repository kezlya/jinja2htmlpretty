# -*- coding: utf-8 -*-
"""
    jinja2htmlpretty
    ~~~~~~~~~~~~~~~~~~

    A Jinja2 extension that pretty prints html at template
    compilation time without extra overhead.

    :copyright: (c) 2016 by Vitaly Kezlya.
    :license: BSD, see LICENSE for more details.
"""
import re
from jinja2.ext import Extension
from jinja2.lexer import Token, describe_token
from jinja2 import TemplateSyntaxError


_tag_re = re.compile(r'(?:<\s*(/?)\s*([a-zA-Z0-9_-]+)\s*|(>\s*))(?s)')
_ws_normalize_re = re.compile(r'[ \t\r\n]+')

_ws_around_equal_re = re.compile(r'[ \t\r\n]*=[ \t\r\n]*"[ \t\r\n]*')
_ws_around_dquotes_re = re.compile(r'[ \t\r\n]+"')
_ws_open_bracket_re = re.compile(r'[ \t\r\n]*<[ \t\r\n]*')
_ws_open_bracket_slash_re = re.compile(r'[ \t\r\n]*<[ \t\r\n]*/[ \t\r\n]*')
_ws_close_bracket_re = re.compile(r'[ \t\r\n]*>[ \t\r\n]*')


class StreamProcessContext(object):

    def __init__(self, stream):
        self.stream = stream
        self.token = None
        self.stack = []

    def fail(self, message):
        raise TemplateSyntaxError(message, self.token.lineno,
                                  self.stream.name, self.stream.filename)

#TODO convert it once when lib included not on every init
def _make_dict_from_listing(listing):
    rv = {}
    for keys, value in listing:
        for key in keys:
            rv[key] = value
    return rv


class HTMLPretty(Extension):
    isolated_elements = set(['script', 'style', 'noscript', 'textarea', 'pre'])
    void_elements = set(['br', 'img', 'area', 'hr', 'param', 'input',
                         'embed', 'col', 'meta', 'link', 'path'])
    block_elements = set(['div', 'p', 'form', 'ul', 'ol', 'li', 'table', 'tr',
                          'tbody', 'thead', 'tfoot', 'tr', 'td', 'th', 'dl',
                          'dt', 'dd', 'blockquote', 'h1', 'h2', 'h3', 'h4',
                          'h5', 'h6', 'pre'])
    #TODO this called on each page, need to extract outside of class
    breaking_rules = _make_dict_from_listing([
        (['p'], set(['#block'])),
        (['li'], set(['li'])),
        (['td', 'th'], set(['td', 'th', 'tr', 'tbody', 'thead', 'tfoot'])),
        (['tr'], set(['tr', 'tbody', 'thead', 'tfoot'])),
        (['thead', 'tbody', 'tfoot'], set(['thead', 'tbody', 'tfoot'])),
        (['dd', 'dt'], set(['dl', 'dt', 'dd']))
    ])

    #TODO move this to __init__
    SHIFT = '  '
    last_tag = ''
    depth = 0
    just_closed = False
    start = True
    ctx = None
    buf = []
    chunk = None
    tag = None
    stack =[]
    lineno = None
    filename = None
    name = None

    def fail(self, message):
        raise TemplateSyntaxError(message, self.lineno,
                                  self.name, self.filename)

    def is_breaking(self, other_tag):
        breaking = self.breaking_rules.get(other_tag)
        return breaking and (self.tag in breaking or
            ('#block' in breaking and self.tag in self.block_elements))

    def is_isolated(self):
        for tag in reversed(self.stack):
            if tag in self.isolated_elements:
                return True
        return False

    def enter_tag(self, tag):
        while self.stack and self.is_breaking(self.stack[-1]):
            self.leave_tag(self.stack[-1])

        if tag == 'br':
            return
        self.last_tag = tag
        if tag in self.void_elements:
            return
        self.stack.append(tag)
        self.depth += 1
        self.just_closed = False

    def leave_tag(self, tag):
        if not self.stack:
            self.fail('Tried to leave "%s" '
                      'but something closed it already' % tag)
        if tag == self.stack[-1]:
            self.stack.pop()
            return
        for idx, other_tag in enumerate(reversed(self.stack)):
            if other_tag == tag:
                for num in xrange(idx + 1):
                    self.stack.pop()
            elif not self.breaking_rules.get(other_tag):
                break

    def adj_depth(self):
        if self.chunk.startswith("</") and self.tag != 'br':
            self.depth -= 1

    def shift(self):
        self.buf.append('\n')
        [self.buf.append(self.SHIFT) for _ in xrange(self.depth)]

    def write(self):
        self.buf.append(self.chunk)

    def check_then_write(self, should_shift):
        if len(self.buf) > 0 and self.buf[-1][-1] == ' ':
            self.buf[-1] = self.buf[-1][:-1]
        if should_shift:
            self.shift()
        self.write()

    def write_preamble(self):
        if self.chunk == '' or self.chunk.strip() == '':
            return
        if not self.is_isolated():
            if self.tag is None:
                self.clean_quotes()
            self.chunk = _ws_normalize_re.sub(' ', self.chunk)
        self.write()

    def write_tag(self):
        self.chunk = _ws_normalize_re.sub(' ', self.chunk)
        self.chunk = _ws_open_bracket_re.sub('<', self.chunk)
        self.check_then_write(self.check_shift())

    def clean_quotes(self):
        self.chunk = _ws_around_equal_re.sub('="', self.chunk)
        self.chunk = _ws_around_dquotes_re.sub('"', self.chunk)

    def check_shift(self):
        if self.tag == 'br':
            return False
        if self.chunk.startswith("</"):
            if self.tag != self.last_tag or self.just_closed:
                return True
            self.just_closed = True
        elif self.chunk.startswith("<"):
            if self.start:
                self.start = False
                if len(self.buf) > 0:
                    return True
            else:
                return True
        return False

    def write_sole(self):
        if not self.is_isolated():
            self.chunk = _ws_close_bracket_re.sub('>', self.chunk)
        self.check_then_write(False)

    def normalize(self, content):
        self.buf = []
        pos = 0
        for match in _tag_re.finditer(content):
            closes, self.tag, sole = match.groups()
            self.chunk = content[pos:match.start()]
            self.write_preamble()
            pos = match.end()
            if sole:
                self.chunk = sole
                self.write_sole()
                continue

            self.chunk = _ws_open_bracket_slash_re.sub('</', match.group())
            self.adj_depth()
            (self.is_isolated() and self.write or self.write_tag)()
            (closes and self.leave_tag or self.enter_tag)(self.tag)

        self.chunk = content[pos:]
        self.write_preamble()
        return

    def filter_stream(self, stream):
        self.name = stream.name
        self.filename = stream.filename
        for token in stream:
            if token.type != 'data':
                yield token
                continue

            self.lineno = token.lineno
            self.normalize(token.value)
            yield Token(token.lineno, 'data', ''.join(self.buf))
