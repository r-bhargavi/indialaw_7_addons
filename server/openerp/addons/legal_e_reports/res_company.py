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
        'cost_report_ids': fields.one2many('legal.cost.report', 'company_id', 'Report Heading'),
        }
    
res_company()


class cost_report(osv.osv):
    
    _name = 'legal.cost.report'
    _order = 'sequence'
    _description = 'Report Heading'
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name', size=32),
        'account_ids': fields.many2many('account.account', 'cost_report_accounts', 'company_id', 'account_id', 'Accounts'),
        
        }
    
cost_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: