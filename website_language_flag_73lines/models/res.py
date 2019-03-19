# -*- coding: utf-8 -*-
##############################################################################
#
#    73Lines Development Pvt. Ltd.
#    Copyright (C) 2009-TODAY 73Lines(<http://www.73lines.com>).
#
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# import odoo
from odoo import fields, models
from odoo.http import request
from odoo.osv import orm


class ResLang(models.Model):
    _inherit = 'res.lang'
    lang_flag = fields.Binary(string='Language Flag')


# class Website(models.Model):
#     _inherit = 'website'
#
#     @odoo.tools.ormcache('id')
#     def _get_languages(self, cr, uid, id, context=None):
#         website = self.browse(cr, uid, id)
#         return [(lg.code, lg.name, lg.direction)
#                 for lg in website.language_ids]
#
#     def get_alternate_languages(self, cr, uid, ids, req=None, context=None):
#         langs = []
#         if req is None:
#             req = request.httprequest
#         default = self.get_current_website(
#             cr, uid, context=context).default_lang_code
#         shorts = []
#
#         def get_url_localized(router, lang):
#             arguments = dict(request.endpoint_arguments)
#             for k, v in arguments.items():
#                 if isinstance(v, orm.browse_record):
#                     arguments[k] = v.with_context(lang=lang)
#             return router.build(request.endpoint, arguments)
#
#         router = request.httprequest.app.get_db_router(request.db).bind('')
#         for code, name, direction in self.get_languages(
#                 cr, uid, ids, context=context):
#             lg_path = ('/' + code) if code != default else ''
#             lg = code.split('_')
#             shorts.append(lg[0])
#             uri = request.endpoint and get_url_localized(
#                 router, code) or request.httprequest.path
#             if req.query_string:
#                 uri += '?' + req.query_string
#             lang = {
#                 'hreflang': ('-'.join(lg)).lower(),
#                 'short': lg[0],
#                 'href': req.url_root[0:-1] + lg_path + uri,
#             }
#             langs.append(lang)
#         for lang in langs:
#             if shorts.count(lang['short']) == 1:
#                 lang['hreflang'] = lang['short']
#         return langs
#
#
# class IrHttp(models.TransientModel):
#     _inherit = 'ir.http'
#
#     def get_nearest_lang(self, lang):
#         # super(IrHttp, self).get_nearest_lang(lang=lang)
#         # Try to find a similar lang. Eg: fr_BE and fr_FR
#         short = lang.partition('_')[0]
#         short_match = False
#         for code, name, direction in request.website.get_languages():
#             if code == lang:
#                 return lang
#             if not short_match and code.startswith(short):
#                 short_match = code
#         return short_match
