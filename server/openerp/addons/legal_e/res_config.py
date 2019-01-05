# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class legale_config_settings(osv.osv_memory):
    _name = 'legale.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'module_customer_receivable_account': fields.boolean('Create Customer Receivable Account'),
        'module_hr_birthdays_dashboard': fields.boolean('Create Employee Birthday\'s Dashboard'),
    }

    def create(self, cr, uid, values, context=None):
        res_id = super(legale_config_settings, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [res_id], vals, context)
        return res_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: