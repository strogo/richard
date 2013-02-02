# richard -- video index system
# Copyright (C) 2012, 2013 richard contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from haystack.views import SearchView, search_view_factory
from haystack.forms import ModelSearchForm
from tastypie.api import Api

from richard.videos.api import VideoResource, CategoryResource
from richard.videos.feeds import (CategoryVideosFeed, SpeakerVideosFeed,
                                  NewPostedVideoFeed)


urlpatterns = patterns(
    'richard.videos.views',

    # categories
    url(r'^category/?$',
        'category_list', name='videos-category-list'),
    url(r'^category/(?P<category_id>[0-9]+)(?:/(?P<slug>[\w-]*))?/?$',
        'category', name='videos-category'),
    url(r'^category/(?P<category_id>[0-9]+)(?:/(?P<slug>[\w-]*))?/rss/?$',
        CategoryVideosFeed(), name='videos-category-feed'),
    url(r'^category/(?P<category_id>[0-9]+)(?:/(?P<slug>[\w-]*))?/files/?$',
        'category_files', name='videos-category-files'),

    # speakers
    url(r'^speaker/$',
        'speaker_list', name='videos-speaker-list'),
    url(r'^speaker/(?P<speaker_id>[0-9]+)(?:/(?P<slug>[\w-]*))?/?$',
        'speaker', name='videos-speaker'),
    url(r'^speaker/(?P<speaker_id>[0-9]+)(?:/(?P<slug>[\w-]*))?/rss/?$',
        SpeakerVideosFeed(), name='videos-speaker-feed'),

    # videos
    url(r'^video/(?P<video_id>[0-9]+)(?:/(?P<slug>[\w-]*))?/?$',
        'video', name='videos-video'),
    url(r'^video/rss/?$', NewPostedVideoFeed(), name='videos-new-feed'),

    # search
    url(r'^search/?$',
        search_view_factory(
            view_class=SearchView,
            template='videos/search.html',
            form_class=ModelSearchForm),
        name='haystack-search'),
    url(r'^search/xml/?$',
        'opensearch', name='videos-opensearch'),
    url(r'^search/suggestions/$',
        'opensearch_suggestions', name='videos-opensearch-suggestions'),

    # faux api for carl
    url(r'^api/1.0/videos/urlforsource$',
        'apiurlforsource', name='videos-api-urlforsource'),
)


def build_api_urls():
    v1_api = Api(api_name='v1')
    v1_api.register(VideoResource())
    v1_api.register(CategoryResource())

    return patterns(
        'richard.videos.views',

        (r'^api/', include(v1_api.urls)),
        )


# API is disabled by default. To enable it, add ``API = True`` to your
# settings.py file.
if settings.API:
    urlpatterns += build_api_urls()
