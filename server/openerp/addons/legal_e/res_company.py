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

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'company_pan_no': fields.char('PAN Number',size=40),
        'expense_account_ids': fields.many2many('account.account','company_accounts', 'company_id', 'account_id', 'Expense Accounts'),
        'proceed_stage_id': fields.many2one('court.proceedings.stage', 'Closing Stage'),
        }
    
res_company()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: