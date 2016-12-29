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

    SHIFT = u'  '
    last_tag = ''
    depth = 0
    just_closed = False
    start = True
    ctx = None

    def is_isolated(self):
        for tag in reversed(self.ctx.stack):
            if tag in self.isolated_elements:
                return True
        return False

    def is_breaking(self, tag, other_tag):
        breaking = self.breaking_rules.get(other_tag)
        return breaking and (tag in breaking or
            ('#block' in breaking and tag in self.block_elements))

    def enter_tag(self, tag):
        while self.ctx.stack and self.is_breaking(tag, self.ctx.stack[-1]):
            self.leave_tag(self.ctx.stack[-1])

        if tag != 'br':
            self.last_tag = tag
            if tag not in self.void_elements:
                self.ctx.stack.append(tag)

                self.depth += 1
                self.just_closed = False

    def leave_tag(self, tag):
        if not self.ctx.stack:
            self.ctx.fail('Tried to leave "%s" but something closed '
                     'it already' % tag)
        if tag == self.ctx.stack[-1]:
            self.ctx.stack.pop()
            return
        for idx, other_tag in enumerate(reversed(self.ctx.stack)):
            if other_tag == tag:
                for num in xrange(idx + 1):
                    self.ctx.stack.pop()
            elif not self.breaking_rules.get(other_tag):
                break

    def normalize(self, ctx):
        pos = 0
        buffer = []
        self.ctx = ctx

        def shift():
            buffer.append(u'\n')
            [buffer.append(self.SHIFT) for _ in xrange(self.depth)]

        def write_preamble(p, tag):
            if p == '' or p.strip() == '':
                return

            if not self.is_isolated():
                if tag is None:
                    p = _ws_around_equal_re.sub('="', p)
                    p = _ws_around_dquotes_re.sub('"', p)
                p = _ws_normalize_re.sub(' ', p)

            buffer.append(p)

        def write_tag(v, tag, closes):
            should_shift = False
            if not self.is_isolated():
                v = _ws_normalize_re.sub(' ', v)
                v = _ws_open_bracket_re.sub('<', v)
                v = _ws_open_bracket_slash_re.sub('</', v)

                if tag != 'br':
                    if v.startswith("</"):
                        self.depth -= 1
                        if tag != self.last_tag or self.just_closed:
                            should_shift = True
                        else:
                            self.just_closed = True
                    elif v.startswith("<"):
                        if self.start:
                            self.start = False
                            if len(buffer) > 0:
                                should_shift = True
                        else:
                            should_shift = True

                if should_shift:
                    shift()
                    buffer.append(v)
                else:
                    check_then_write(v)
            else:
                if v.startswith("</"):
                    self.depth -= 1
                buffer.append(v)

            (closes and self.leave_tag or self.enter_tag)(tag)

        def write_sole(s):
            if not self.is_isolated():
                s = _ws_close_bracket_re.sub('>', s)
            check_then_write(s)

        def check_then_write(v):
            if len(buffer) > 0 and buffer[-1][-1] == ' ':
                buffer[-1] = buffer[-1][:-1] + v
            else:
                buffer.append(v)

        for match in _tag_re.finditer(ctx.token.value):
            closes, tag, sole = match.groups()
            preamble = ctx.token.value[pos:match.start()]
            write_preamble(preamble, tag)
            if sole:
                write_sole(sole)
            else:
                write_tag(match.group(), tag, closes)
            pos = match.end()
        write_preamble(ctx.token.value[pos:], None)
        return u''.join(buffer)

    def filter_stream(self, stream):
        ctx = StreamProcessContext(stream)
        for token in stream:
            if token.type != 'data':
                yield token
                continue
            ctx.token = token
            value = self.normalize(ctx)
            yield Token(token.lineno, 'data', value)
