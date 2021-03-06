# -*- encoding: utf-8 -*-

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2015 David Fischer. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of David Fischer's pytoolbox Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/davidfischer-ch/pytoolbox.git

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from django.contrib.sites.models import Site
from django.core.urlresolvers import resolve, reverse
from django.db import connections, DEFAULT_DB_ALIAS
from django.test.utils import CaptureQueriesContext

from ...encoding import string_types

__all__ = ('ClearSiteCacheMixin', 'FormWizardMixin', 'QueriesMixin', 'UrlMixin', 'RestAPIMixin')


class _AssertNumQueriesInContext(CaptureQueriesContext):

    def __init__(self, test_case, num_range, connection):
        self.test_case = test_case
        self.range = num_range
        super(_AssertNumQueriesInContext, self).__init__(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        super(_AssertNumQueriesInContext, self).__exit__(exc_type, exc_value, traceback)
        if exc_type is None:
            executed = len(self)
            self.test_case.assertIn(
                executed, self.range, '{1} queries executed, {2.range} expected{0}Captured queries were:{0}{3}'.format(
                    os.linesep, executed, self, os.linesep.join(query['sql'] for query in self.captured_queries)
                )
            )


class ClearSiteCacheMixin(object):

    def clear_site_cache(self):
        Site.objects.clear_cache()

    def setUp(self):
        self.clear_site_cache()
        super(ClearSiteCacheMixin, self).setUp()

    def assertNumQueries(self, *args, **kwargs):
        self.clear_site_cache()
        return super(ClearSiteCacheMixin, self).assertNumQueries(*args, **kwargs)


class FormWizardMixin(object):

    def post_wizard(self, url, step, data=None, raw_data=None, **kwargs):
        from formtools.wizard.views import normalize_name
        name = normalize_name(resolve(reverse(url)).func.__name__)
        step_data = {'{0}-{1}'.format(step, k): v for k, v in data.items()} if data else {}
        step_data['{0}-current_step'.format(name)] = step
        step_data.update(raw_data or {})
        return self.post(url, step_data, **kwargs)


class QueriesMixin(object):

    def assertNumQueriesIn(self, num_range, func=None, *args, **kwargs):
        connection = connections[kwargs.pop('using', DEFAULT_DB_ALIAS)]
        context = _AssertNumQueriesInContext(self, num_range, connection)
        if func is None:
            return context
        with context:
            func(*args, **kwargs)


class UrlMixin(object):

    def resolve(self, value, qs=None, urlconf=None, args=None, kwargs=None, current_app=None):
        if isinstance(value, string_types) and '/' in value:
            url = value
        elif hasattr(value, 'get_absolute_url'):
            url = value.get_absolute_url()
        else:
            url = reverse(value, urlconf, args, kwargs, current_app)
        return url if qs is None else '{0}?{1}'.format(url, qs)


class RestAPIMixin(UrlMixin):

    def _call(self, method, url, data, status, qs=None, urlconf=None, args=None, kwargs=None, current_app=None,
              msg=lambda r: getattr(r, 'data', r), **call_kwargs):
        url = self.resolve(url, qs, urlconf, args, kwargs, current_app)
        response = getattr(self.client, method)(url, data, **call_kwargs)
        self.assertEqual(response.status_code, status, msg(response))
        return response

    def delete(self, url, data=None, status=204, **kwargs):
        return self._call('delete', url, data, status, **kwargs)

    def get(self, url, data=None, status=200, **kwargs):
        return self._call('get', url, data, status, **kwargs)

    def patch(self, url, data, status=200, **kwargs):
        return self._call('patch', url, data, status, **kwargs)

    def post(self, url, data, status=201, **kwargs):
        return self._call('post', url, data, status, **kwargs)

    def put(self, url, data, status=200, **kwargs):
        return self._call('put', url, data, status, **kwargs)
