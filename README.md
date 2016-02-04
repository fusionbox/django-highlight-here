# django-highlighthere

Templatetags to add a 'here' classes to anchors where appropriate, based on
startswith matching. Taken straight from the `django-fusionbox` package.

## Examples

Given:

    {% highlight_here %}
        <a href="/" class="home">/</a>
        <a href="/blog/">blog</a>
    {% endhighlight %}

If request.url is ``/``, the output is:

    <a href="/" class="home here">/</a>
    <a href="/blog/">blog</a>

On ``/blog/``, it is:

    <a href="/" class="home">/</a>
    <a href="/blog/" class="here">blog</a>


Given:

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

If request.url is ``/``, the output is:

    <ul>
        <li id="navHome" class="parent_home here">
            <a href="/" class="home">/</a>
        </li>
        <li>
            <a href="/blog/">blog</a>
        </li>
    <ul>

