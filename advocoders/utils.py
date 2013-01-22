import feedparser
from dateutil.parser import parse as dateutil_parse
from BeautifulSoup import BeautifulSoup
import pygments
import pygments.formatters
import pygments.lexers
from advocoders.models import Content
from advocoders.models import Profile


def update_feeds(*args, **kwargs):
    for profile in Profile.objects.all():
        for provider, rss_url in profile.rss_urls:

            Content.objects.filter(
                user=profile.user,
                provider=provider).delete()

            print rss_url
            feed = feedparser.parse(rss_url)
            for entry in feed.get('entries')[:10]:
                content = Content()
                content.user = profile.user
                content.provider = provider
                content.title = entry.title
                content.link = entry.link
                content.date = dateutil_parse(entry.updated)
                content.mime_type, content.body = get_body_and_mime_type(entry)
                if content.mime_type == 'text/html':
                    klass = 'code' if provider == 'stackoverflow' else 'pre'
                    content.body = highlight_code_inside_html(content.body, klass)
                content.save()


def get_body_and_mime_type(entry):
    try:
        return entry.content[0].type, entry.content[0].value
    except AttributeError:
        return 'text/html', entry.summary


def get_domain(email):
    return email.split('@')[1]


def highlight_code_inside_html(html, klass='pre'):
    ''' from: http://stefan.sofa-rockers.org/2010/01/13/django-highlighting-html-using-pygments-and-beauti '''
    soup = BeautifulSoup(html)
    codeblocks = soup.findAll(klass)
    for block in codeblocks:
        try:
            code = ''.join([unicode(item) for item in block.contents])
            lexer = pygments.lexers.guess_lexer(code)
            formatter = pygments.formatters.HtmlFormatter()
            code_hl = pygments.highlight(code, lexer, formatter)
            block.contents = [BeautifulSoup(code_hl)]
            block.name = 'code'
        except Exception, e:
            print 'Exception in highlight_code_inside_html: %s' % e
    return unicode(soup)
