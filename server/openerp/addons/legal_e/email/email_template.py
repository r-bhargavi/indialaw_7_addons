# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Sharoon Thomas
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import base64
import logging
from urllib import urlencode, quote as quote

from openerp import netsvc
from openerp.osv import osv
from openerp import tools


_logger = logging.getLogger(__name__)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")

class email_template(osv.osv):
    "Templates for sending email"
    _inherit = "email.template"
    _description = 'Email Templates'
    _order = 'name'

    def generate_email(self, cr, uid, template_id, res_id, context=None):
        """Generates an email from the template for given (model, res_id) pair.

           :param template_id: id of the template to render.
           :param res_id: id of the record to use for rendering the template (model
                          is taken from template definition)
           :returns: a dict containing all relevant fields for creating a new
                     mail.mail entry, with one extra key ``attachments``, in the
                     format expected by :py:meth:`mail_thread.message_post`.
        """
        if context is None:
            context = {}
        report_xml_pool = self.pool.get('ir.actions.report.xml')
        template = self.get_email_template(cr, uid, template_id, res_id, context)
        values = {}
        for field in ['subject', 'body_html', 'email_from',
                      'email_to', 'email_recipients', 'email_cc', 'reply_to']:
            if context.has_key(field):
                values[field] = context[field]    
            else:    
                values[field] = self.render_template(cr, uid, getattr(template, field),
                                                 template.model, res_id, context=context) \
                                                 or False
        if template.user_signature:
            signature = self.pool.get('res.users').browse(cr, uid, uid, context).signature
            values['body_html'] = tools.append_content_to_html(values['body_html'], signature)

        if values['body_html']:
            values['body'] = tools.html_sanitize(values['body_html'])

        values.update(mail_server_id=template.mail_server_id.id or False,
                      auto_delete=template.auto_delete,
                      model=template.model,
                      res_id=res_id or False)

        attachments = []
        # Add report in attachments
        if template.report_template:
            report_name = self.render_template(cr, uid, template.report_name, template.model, res_id, context=context)
            report_service = 'report.' + report_xml_pool.browse(cr, uid, template.report_template.id, context).report_name
            # Ensure report is rendered using template's language
            ctx = context.copy()
            if template.lang:
                ctx['lang'] = self.render_template(cr, uid, template.lang, template.model, res_id, context)
            service = netsvc.LocalService(report_service)
            (result, format) = service.create(cr, uid, [res_id], {'model': template.model}, ctx)
            result = base64.b64encode(result)
            if not report_name:
                report_name = report_service
            ext = "." + format
            if not report_name.endswith(ext):
                report_name += ext
            attachments.append((report_name, result))

        attachment_ids = []
        # Add template attachments
        for attach in template.attachment_ids:
            attachment_ids.append(attach.id)

        values['attachments'] = attachments
        values['attachment_ids'] = attachment_ids
        return values
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
