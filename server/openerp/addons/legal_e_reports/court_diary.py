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
from openerp.osv import osv


class court_diary(osv.osv_memory):
    _inherit = "court.diary"
    
            
    def print_mis_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids,)[-1]
        report = {
            'type': 'ir.actions.report.xml',
            'report_name': 'jasper_mis_report',
            'name': 'MIS',
            'datas': {
                'model':'court.proceedings',
                'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                'ids': context.get('active_ids') and context.get('active_ids') or [],
                'report_type': 'xls',
                'form': data,
                },
            'nodestroy': False
            }
        return report
    

court_diary()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: