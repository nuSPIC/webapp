import re
from django.conf import settings
from django.utils.html import escape
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe


__all__ = ('BBCODE_RULES', 'bbcode')

#regexp for url validation from django URLField + added ftp:// and allowing spaces around
URL_RE = r'\s*((ftp|https?)://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'\
    'localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+))\s*'

#regexp for email from django + allowing spaces around
EMAIL_RE = r"""\s*(([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^"""\
        """([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")"""\
        """@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?)\s*"""


def code_parser(matchobj):
    """
    Escaping bbcode and html tags between [code] tags.
    """

    value = matchobj.group(1)
    value = value.replace('[', '&#91;')
    value = value.replace(']', '&#93;')
    value = value.replace('<br />', '\n')
    return "<pre><code>%s</code></pre>" % value

"""
BBcode rule format:
    'pattern' and 'repl'' - params for re.sub(); 'repl' can be function
    'sortkey' - used to sort rules from highest to lowest; default value: 0
    'nested' - show how many time tag can be nested to itself; only for [quote] now
"""

BBCODE_RULES = [
        {'pattern': r'\[code\](.*?)\[/code\]', 'repl': code_parser, 'sortkey': 100},
        {'pattern': r'\[url\]%s\[/url\]' % URL_RE, 'repl': r'<a href="\1">\1</a>'},
        {'pattern': r'\[url=%s\](.*?)\[/url\]' % URL_RE, 'repl': r'<a href="\1">\3</a>'},
        {'pattern': r'\[link\]%s\[/link\]' % URL_RE, 'repl': r'<a href="\1">\1</a>'},
        {'pattern': r'\[link=%s\](.*?)\[/link\]' % URL_RE, 'repl': r'<a href="\1">\3</a>'},
        {'pattern': r'\[email\]%s\[/email\]' % EMAIL_RE, 'repl': r'<a href="mailto:\1">\1</a>'},
        {'pattern': r'\[email=%s\](.*?)\[/email\]' % EMAIL_RE, 'repl': r'<a href="mailto:\1">\5</a>'},
        {'pattern': r'\[img\]%s\[/img\]' % URL_RE, 'repl': r'<img src="\1">'},
        {'pattern': r'\[img=%s\](.*?)\[/img\]' % URL_RE, 'repl': r'<img src="\1" alt="\3">'},
        {'pattern': r'\[color=([a-zA-Z]*|\#?[0-9a-fA-F]{6})\](.*?)\[/color\]', 'repl': r'<span style="color:\1">\2</span>'},
        {'pattern': r'\[b\](.*?)\[/b\]', 'repl': r'<strong>\1</strong>'},
        {'pattern': r'\[i\](.*?)\[/i\]', 'repl': r'<em>\1</em>'},
        {'pattern': r'\[u\](.*?)\[/u\]', 'repl': r'<u>\1</u>'},
        {'pattern': r'\[s\](.*?)\[/s\]', 'repl': r'<strike>\1</strike>'},
        {'pattern': r'\[quote\](.*?)\[/quote\]', 'repl': r'<blockquote>\1</blockquote>', 'nested': 5},
        {'pattern': r'\[quote=(.*?)\](.*?)\[/quote\]', 'repl': r'<blockquote><em>\1</em> <br /> \2</blockquote>', 'nested': 5},
        {'pattern': r'\[center\](.*?)\[/center\]', 'repl': r'<div style="text-align: center;">\1</div>'},
        {'pattern': r'\[big\](.*?)\[/big\]', 'repl': r'<big>\1</big>'},
        {'pattern': r'\[small\](.*?)\[/small\]', 'repl': r'<small>\1</small>'},
        {'pattern': r'\[list\](.*?)\[/list\]', 'repl': r'<ul>\1</ul>'},
        {'pattern': r'\[list\=(\d+)\](.*?)\[/list\]', 'repl': r'<ol start="\1">\2</ol>'},
        {'pattern': r'\[\*\](.*?)<br./>', 'repl': r'<li>\1</li>'},
        {'pattern': r'\[br\]', 'repl': r'<br />'},
]

BBCODE_RULES += getattr(settings, 'BBMARKUP_EXTRA_RULES', [])
BBCODE_RULES.sort(key=lambda r: r.get('sortkey', 0), reverse=True)

BBCODE_RULES_COMPILED = []
for bbset in (getattr(settings, 'BBMARKUP_CUSTOM_RULES', []) or BBCODE_RULES):
    bbset['pattern'] = re.compile(bbset['pattern'], re.DOTALL | re.IGNORECASE)
    bbset.setdefault('sortkey', 0)
    bbset.setdefault('nested', 0)
    BBCODE_RULES_COMPILED.append(bbset)

def bbcode(value, code_parser=code_parser):
    """
    >>> data = '[code]print "Lorem [b]imsum[b]"[/code]'
    >>> bbcode(data)
    u'<pre><code>print &quot;Lorem &#91;b&#93;imsum&#91;b&#93;&quot;</code></pre>'
    >>> bbcode('[i]Lorem[/i] \\n [s]imsum[/s]')
    u'<em>Lorem</em> <br /> <strike>imsum</strike>'
    >>> bbcode('[list] [*] 1\\n [*]2\\n [*] 3\\n[/list]')
    u'<ul> <li> 1</li> <li>2</li> <li> 3</li></ul>'
    >>> bbcode('[list=2] [*] a\\n [*]b\\n [*] c\\n[/list]')
    u'<ol start="2"> <li> a</li> <li>b</li> <li> c</li></ol>'
    >>> bbcode("[code]print 123\\nprint '<br/>'[/code]")
    u'<pre><code>print 123\\nprint &#39;&lt;br/&gt;&#39;</code></pre>'
    >>> bbcode('[quote=test user]Test quote text[/quote]')
    u'<blockquote><em>test user</em> <br /> Test quote text</blockquote>'
    >>> bbcode("[quote]Lorem [quote=sl]imsum[/quote] blabla [/quote]")
    u'<blockquote>Lorem <blockquote><em>sl</em> <br /> imsum</blockquote> blabla </blockquote>'
    >>> bbcode('[color=red]Lorem[/color]')
    u'<span style="color:red">Lorem</span>'
    >>> bbcode('[color=#FAaF12]Lorem[/color]')
    u'<span style="color:#FAaF12">Lorem</span>'
    >>> bbcode('[color=#FAaF121]Lorem[/color]')
    u'[color=#FAaF121]Lorem[/color]'
    >>> bbcode('[url]http://slav0nic.org.ua[/url]]')
    u'<a href="http://slav0nic.org.ua">http://slav0nic.org.ua</a>]'
    >>> bbcode('[url]http://slav0nic.org.ua[/url]')
    u'<a href="http://slav0nic.org.ua">http://slav0nic.org.ua</a>'
    >>> bbcode('[url]  ftp://slav0nic.org.ua/test  [/url]')
    u'<a href="ftp://slav0nic.org.ua/test">ftp://slav0nic.org.ua/test</a>'
    >>> bbcode('[url]  http://slav0nic.org.ua:80/test/foo.py?s=bar#foo1[/url]')
    u'<a href="http://slav0nic.org.ua:80/test/foo.py?s=bar#foo1">http://slav0nic.org.ua:80/test/foo.py?s=bar#foo1</a>'
    >>> bbcode('[link=http://test.com/] test [/link]')
    u'<a href="http://test.com/"> test </a>'
    >>> bbcode('[url= http://test.com/  ] test [/url]')
    u'<a href="http://test.com/"> test </a>'
    >>> bbcode('[url= http://test.com/][/url]')
    u'<a href="http://test.com/"></a>'
    >>> bbcode('[img]  https://slav0nic.org.ua:80/test/logo.png [/img]')
    u'<img src="https://slav0nic.org.ua:80/test/logo.png">'
    >>> bbcode('[img]javascript:alert("XSS");[/img]')
    u'[img]javascript:alert("XSS");[/img]'
    >>> bbcode('''[email]blabla@test.com" onmouseover="alert('Hacked');[/email]''')
    u'[email]blabla@test.com&quot; onmouseover=&quot;alert(&#39;Hacked&#39;);[/email]'
    >>> bbcode('[email]  blabla@test.com   [/email]')
    u'<a href="mailto:blabla@test.com">blabla@test.com</a>'
    >>> bbcode('[email]blabla@test.com[/email]')
    u'<a href="mailto:blabla@test.com">blabla@test.com</a>'
    >>> bbcode('[email=  blabla@test.com  ] Blablasha :][/email]')
    u'<a href="mailto:blabla@test.com"> Blablasha :]</a>'
    """

    value = escape(value)
    value = linebreaksbr(value)
    for bbset in BBCODE_RULES_COMPILED:
        for _ in xrange(bbset['nested'] + 1):
            value = bbset['pattern'].sub(bbset['repl'], value)

    return mark_safe(value)
