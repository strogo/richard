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

from django.core.urlresolvers import reverse
from django.test import TestCase

from nose.tools import eq_

from richard.suggestions.models import Suggestion
from richard.suggestions.tests import suggestion


class TestSuggestions(TestCase):
    """Tests for the ``suggestions`` app."""

    def test_not_reviewed_list(self):
        """Test the view of the listing of all suggestions."""
        url = reverse('suggestions-list')
        s = suggestion(save=True)

        resp = self.client.get(url)
        eq_(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'suggestions/suggestions_list.html')
        assert s.name not in resp.content

    def test_reviewed_list(self):
        """Test the view of the listing of all suggestions."""
        url = reverse('suggestions-list')
        s = suggestion(save=True)
        s.is_reviewed = True
        s.save()

        resp = self.client.get(url)
        eq_(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'suggestions/suggestions_list.html')
        assert s.name in resp.content

    def test_list_without_spam(self):
        """Test that entries marked as spam do not show up."""
        url = reverse('suggestions-list')
        s = suggestion(state=Suggestion.STATE_SPAM, save=True)

        resp = self.client.get(url)
        eq_(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'suggestions/suggestions_list.html')
        assert s.name not in resp.content

    def test_submit(self):
        """Test that submitting a suggestion works."""
        url = reverse('suggestions-list')

        resp = self.client.post(url, {'name': u'Add boston user group',
                                      'url': u'http://meetup.bostonpython.com/'},
                                follow=True)
        eq_(resp.status_code, 200)
        assert Suggestion.objects.filter(name=u'Add boston user group').exists()
