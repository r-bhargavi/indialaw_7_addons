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

import time
from openerp.report import report_sxw
from datetime import datetime


class consolidated_bill(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(consolidated_bill, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'get_date':self.get_date,
            'get_stages':self.get_stages,
        })
        
    def get_date(self, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dt = datetime.strftime(dt, "%d-%b-%y")
        return dt
    
    def get_stages(self, lines):
        stages = ''
        for data_obj in lines.invoice_lines_fixed:
            stages += data_obj.name + '\n'
        for data_obj in lines.invoice_lines_other_expenses:
            stages += data_obj.name + '\n'
        return stages
    
report_sxw.report_sxw('report.consolidated.bill.annexure', 'consolidated.bill', 'addons/legal_e/report/consolidate_bill.rml', parser=consolidated_bill, header=False)
report_sxw.report_sxw('report.consolidated.annexure.bill', 'consolidated.bill', 'addons/legal_e/report/consolidated_annexure_report.rml', parser=consolidated_bill, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: