from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('WSP.rdfedit.views',
    url(r'^index/$', 'index', name='index'),
    url(r'^delete/$', 'delete', name='delete'),
    url(r'^(?P<doc_id>\d+)/spo/$', 'spo', name='spo'),
    url(r'^(?P<rdfxml_id>\d+)/rdf/$', 'rdf', name='rdf'),
)
