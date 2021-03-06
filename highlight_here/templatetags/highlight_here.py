from bs4 import BeautifulSoup
import warnings

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


register = template.Library()

def addclass(elem, cls):
    elem['class'] = elem.get('class', '')
    elem['class'] += ' ' + cls if elem['class'] else cls


def is_here(current, url):
    """
    Determine if current is 'underneath' url.
    """
    if url == '/':
        return current == '/'
    if current.startswith(url):
        return True
    else:
        return False


class HighlighterBase(template.Node):
    """
    Base class for templatetags that highlight specific DOM elements.

    Child classes must implement a ``elems_to_highlight`` method, which should
    return a iterable of elements to modify.  Optionally, they can override the
    ``highlight`` method, which by default simply adds a class to the DOM
    elements.

    Each templatetag accepts an optional ``self.highlight_class`` parameter and
    all other options are stored in ``self.options``.  This behavior can be
    overriden by implementing the ``parse_options`` method.
    """
    def __init__(self, parser, token):
        self.parse_options(token.split_contents())

        self.nodelist = parser.parse(('endhighlight',))
        parser.delete_first_token()

    def parse_options(self, tokens):
        self.options = tokens[1:]
        try:
            self.highlight_class = self.options.pop(0).replace('"', '')
        except IndexError:
            self.highlight_class = None

    def elems_to_highlight(self, soup, context):
        """
        Returns an iterable of all DOM elements to be highlighted.

        Accepts a BeautifulSoup object of the HTML
        """
        raise NotImplemented

    def build_soup(self, context):
        content = self.nodelist.render(context)
        soup = BeautifulSoup(content, "html.parser")

        return soup

    def highlight(self, elem):
        addclass(elem, self.highlight_class)

    def render(self, context):
        soup = self.build_soup(context)

        try:
            for elem in self.elems_to_highlight(soup, context):
                self.highlight(elem)
        except ImproperlyConfigured as e:
            if settings.DEBUG:
                raise
            else:
                # This is because the django 500 error view does not use a
                # request context. We still need to be able to render some kind
                # of error page, so we'll just return our contents unchanged.
                warnings.warn(e.args[0])

        return str(soup)


class HighlightHereNode(HighlighterBase):
    """
    Filter the subnode's output to add a 'here' class to every anchor where
    appropriate, based on startswith matching.

    Given::

        {% highlight_here %}
            <a href="/" class="home">/</a>
            <a href="/blog/">blog</a>
        {% endhighlight %}

    If request.url is ``/``, the output is::

        <a href="/" class="home here">/</a>
        <a href="/blog/">blog</a>

    On ``/blog/``, it is::

        <a href="/" class="home">/</a>
        <a href="/blog/" class="here">blog</a>

    """
    def __init__(self, parser, token):
        super(HighlightHereNode, self).__init__(parser, token)

        self.highlight_class = self.highlight_class or 'here'

    def elems_to_highlight(self, soup, context):
        try:
            path = template.Variable(self.options[0]).resolve(context)
        except template.VariableDoesNotExist:
            path = self.options[0]
        except IndexError:
            if 'request' in context:
                path = context['request'].path
            else:
                raise ImproperlyConfigured(
                    "The request was not available in the context, please "
                    "ensure that the request is made available in the context."
                )

        return (anchor for anchor in soup.findAll('a', {'href': True})
                if is_here(path, anchor['href']))

register.tag("highlight_here", HighlightHereNode)


class HighlightHereParentNode(HighlightHereNode):
    """
    Adds a here class to the parent of the anchor link.  Useful for nested navs
    where highlight style might bubble upwards.

    Given::

        {% highlight_here_parent %}
         <ul>
            <li id="navHome" class="parent_home">
                <a href="/" class="home">/</a>
            </li>
            <li id="navblog" class="">
                <a href="/blog/">blog</a>
            </li>
         </ul>
        {% endhighlight %}

    If request.url is ``/``, the output is::

        <ul>
            <li id="navHome" class="parent_home here">
                <a href="/" class="home">/</a>
            </li>
            <li>
                <a href="/blog/">blog</a>
            </li>
        <ul>

    """
    def elems_to_highlight(self, soup, href):
        anchors = super(HighlightHereParentNode, self).elems_to_highlight(
            soup, href
        )
        for anchor in anchors:
            yield anchor.parent

register.tag("highlight_here_parent", HighlightHereParentNode)
