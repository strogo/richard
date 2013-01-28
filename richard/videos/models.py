# richard -- video index system
# Copyright (C) 2012 richard contributors.  See AUTHORS.
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

import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from richard.videos.utils import generate_unique_slug


MIMETYPES_MAP = {
    'ogv': 'video/ogg',
    'mp4': 'video/mp4',
    'webm': 'video/webm',
    'flv': 'video/x-flv'
}
USE_MARKDOWN_HELP_TEXT = _(u'Use Markdown')


class Category(models.Model):
    title = models.CharField(
        max_length=255,
        help_text=_(u'The complete title for the category. e.g. '
        'PyCon 2010'))
    description = models.TextField(
        blank=True, default=u'',
        help_text=USE_MARKDOWN_HELP_TEXT)
    url = models.URLField(
        blank=True, default=u'',
        help_text=_(u'URL for the category. e.g. If this category was a '
        'conference, this would be the url for the conference '
        'web-site.'))
    start_date = models.DateField(
        blank=True, null=True,
        help_text=_(u'If the category was an event, then this is the start '
        'date for the event.'))

    whiteboard = models.CharField(
        blank=True, max_length=255, default=u'',
        help_text=_(u'Editor notes for this category.'))

    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Category %s>' % self.title.encode('ascii', 'ignore')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, u'title', u'slug')
        super(Category, self).save(*args, **kwargs)

    class Meta(object):
        ordering = ["title"]
        verbose_name = _(u'category')
        verbose_name_plural = _(u'categories')

    @models.permalink
    def get_absolute_url(self):
        return ('videos-category', (self.pk, self.slug))


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Speaker %s: %s>' % (self.id, self.name.encode('ascii', 'ignore'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, u'name', u'slug')
        super(Speaker, self).save(*args, **kwargs)

    class Meta(object):
        ordering = ['name']
        verbose_name = _(u'speaker')
        verbose_name_plural = _(u'speakers')

    @models.permalink
    def get_absolute_url(self):
        return ('videos-speaker', (self.pk, self.slug))


class Tag(models.Model):
    tag = models.CharField(max_length=30)

    def __unicode__(self):
        return self.tag

    def __repr__(self):
        return '<Tag %s>' % self.tag.encode('ascii', 'ignore')

    class Meta(object):
        ordering = ['tag']
        verbose_name = _(u'tag')
        verbose_name_plural = _(u'tags')


class Language(models.Model):
    iso639_1 = models.CharField(max_length=3)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class VideoManager(models.Manager):
    def live(self):
        return self.get_query_set().filter(state=Video.STATE_LIVE)


class Video(models.Model):
    STATE_LIVE = 1
    STATE_DRAFT = 2

    STATE_CHOICES = (
        (STATE_LIVE, u'Live'),
        (STATE_DRAFT, u'Draft'),
        )

    LOCAL_THUMBNAIL_PATH = 'video/thumbnails/%d.jpg'

    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_DRAFT)

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, default=u'',
                               help_text=USE_MARKDOWN_HELP_TEXT)
    description = models.TextField(blank=True, default=u'',
                                   help_text=USE_MARKDOWN_HELP_TEXT)
    tags = models.ManyToManyField(Tag, blank=True)
    category = models.ForeignKey(Category)
    speakers = models.ManyToManyField(Speaker, blank=True)

    # notes for quality issues (audio or video) in the video
    quality_notes = models.TextField(blank=True, default=u'')

    # the primary language the video is in
    language = models.ForeignKey(Language, null=True)

    # text for copyright/license--for now it's loose form.
    # if null, use source video link.
    # TODO: rename this to license
    copyright_text = models.TextField(null=True, blank=True)

    # embed for flash player things
    embed = models.TextField(null=True, blank=True)

    # url for the thumbnail
    thumbnail_url = models.URLField(max_length=255, null=True, blank=True)

    # TODO: fix this--there should be one duration in seconds and then
    # each video type should have a filesize

    # TODO: add video_m4v

    # these are downloadable urls
    video_ogv_length = models.IntegerField(null=True, blank=True)
    video_ogv_url = models.URLField(max_length=255, null=True, blank=True)
    video_ogv_download_only = models.BooleanField(default=False)
    video_mp4_length = models.IntegerField(null=True, blank=True)
    video_mp4_url = models.URLField(max_length=255, null=True, blank=True)
    video_mp4_download_only = models.BooleanField(default=False)
    video_webm_length = models.IntegerField(null=True, blank=True)
    video_webm_url = models.URLField(max_length=255, null=True, blank=True)
    video_webm_download_only = models.BooleanField(default=False)
    video_flv_length = models.IntegerField(null=True, blank=True)
    video_flv_url = models.URLField(max_length=255, null=True, blank=True)
    video_flv_download_only = models.BooleanField(default=False)

    # source url in case we need to find things again
    source_url = models.URLField(max_length=255, null=True, blank=True)

    # whiteboard for editor notes
    whiteboard = models.CharField(max_length=255, blank=True, default=u'')

    # when the video was originally recorded
    recorded = models.DateField(null=True, blank=True)

    # when the video was added to this site
    added = models.DateTimeField(auto_now_add=True)

    # when the video metadata was last updated
    updated = models.DateTimeField(auto_now=True)

    slug = models.SlugField(unique=True)

    objects = VideoManager()

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Video %s (%s)>' % (self.title[:30].encode('ascii', 'ignore'),
                                    self.category)

    def save(self, *args, **kwargs):
        if self.title and not self.slug:
            self.slug = generate_unique_slug(self, u'title', u'slug')
        super(Video, self).save(*args, **kwargs)

    class Meta(object):
        get_latest_by = 'recorded'
        ordering = ['-recorded', 'title']
        verbose_name = _(u'video')
        verbose_name_plural = _(u'videos')

    @models.permalink
    def get_absolute_url(self):
        return ('videos-video', (self.pk, self.slug))

    def get_thumbnail_url(self):
        """Find a thumbnail for this video in the following order:

        1. use a local image
        2. use the remote image in `thumbnail_url`
        3. show a placeholder image
        """
        no_thumbnail = settings.STATIC_URL + 'videos/img/no_thumbnail.png'

        local_path = self.LOCAL_THUMBNAIL_PATH % self.pk
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, local_path)):
            return settings.MEDIA_URL + local_path
        else:
            return self.thumbnail_url or no_thumbnail

    @property
    def thumbnail_width(self):
        return settings.VIDEO_THUMBNAIL_SIZE[0]

    @property
    def thumbnail_height(self):
        return settings.VIDEO_THUMBNAIL_SIZE[1]

    def is_live(self):
        return self.state == self.STATE_LIVE

    def get_available_formats(self, html5tag=False):
        """Return formats ordered by MEDIA_PREFERENCE setting.

        Looks through all video_url/video_length fields on the model and
        selects those that are available, i.e. that have a value. The
        elements in the returned list are ordered by their format.

        :arg html5tag: True if this is being used in an html5 video
            tag

        """
        result = []
        for fmt in settings.MEDIA_PREFERENCE:
            # skip unsupported formats
            if not hasattr(self, 'video_%s_url' % fmt):
                continue

            url = getattr(self, 'video_%s_url' % fmt)
            length = getattr(self, 'video_%s_length' % fmt)
            download_only = getattr(self, 'video_%s_download_only' % fmt)

            # If this is for html5 output and this url is for download
            # only then we skip it.
            if html5tag and download_only:
                continue

            try:
                mime_type = MIMETYPES_MAP[fmt]
            except KeyError:
                raise LookupError('No mimetype registered for "%s"' % fmt)

            if url:
                result.append({'url': url, 'length': length,
                                'mime_type': mime_type})

        if not html5tag:
            # Now we do this goofy thing where if this is a YouTube
            # video we add it to the list of available formats. That's
            # because this gets used to build the enclosures for a
            # feed and we want to make sure this works with Miro.
            #
            # We put it last in the list because most options are
            # better than this one.
            if self.source_url and 'youtube' in self.source_url.lower():
                result.append({'url': self.source_url,
                               'mime_type': 'video/flv'})

        return result


class RelatedUrl(models.Model):
    video = models.ForeignKey(Video, related_name='related_urls')
    url = models.URLField(max_length=255)
    description = models.CharField(max_length=255, blank=True, default=u'')

    def __unicode__(self):
        return self.url

    def __repr__(self):
        return '<URL %s>' % self.url

    def display(self):
        """For showing the url

        This reduces long urls to 50 characters for display.

        """
        return self.url[:50]
