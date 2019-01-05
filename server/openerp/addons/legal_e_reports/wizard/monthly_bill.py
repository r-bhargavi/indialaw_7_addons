# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import osv, fields


class monthly_bill(osv.osv_memory):
    _name = "legal.monthly.bill"
    _description = 'Monthly Bill Details'
    
    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'client_service_manager_id': fields.many2one('hr.employee','Client Relationship Manager'),
        'state_id':fields.many2one('res.country.state', string='State'),
        'ho_branch_id':fields.many2one('ho.branch','Location'),
        
        }
            
    def print_monthly_bill_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids,)[-1]
        report = {
            'type': 'ir.actions.report.xml',
            'report_name': 'jasper_monthly_bill',
            'name': 'Monthly Bill',
            'datas': {
                'model':'legal.monthly.bill',
                'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                'ids': context.get('active_ids') and context.get('active_ids') or [],
                'report_type': 'xls',
                'form': data,
                },
            'nodestroy': False
            }
        return report
    

monthly_bill()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: