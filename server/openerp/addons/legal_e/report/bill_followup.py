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
from datetime import datetime
from openerp.report import report_sxw

class print_bill_followup(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(print_bill_followup, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'get_date':self.get_date,
            'get_lines':self.get_lines,
            'get_lines_llp': self.get_lines_llp,
        })
    
    
    
    
    def get_lines(self, lines):
        res = []
        sl_no = 0
        for line in lines:
            sl_no = sl_no+1
            data = {'sl_no':sl_no,'name':line.name,'date':line.date}
            res.append(data)
        for i in range(1,21):
            res.append({'sl_no':'','name':'','date':''})
        return res
    
    def get_lines_llp(self, lines):
        res = []
        sl_no = 0
        for line in lines:
            sl_no = sl_no+1
            data = {'sl_no':sl_no,'name':line.name,'date':line.date}
            res.append(data)
        for i in range(1,21):
            res.append({'sl_no':'','name':'','amount':''})
        return res
    
        
    def get_date(self, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dt = datetime.strftime(dt, "%d-%m-%y")
        return dt
    

report_sxw.report_sxw('report.bill.followup', 'consolidated.bill', 'addons/legal_e/report/bill_followup.rml', parser=print_bill_followup, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: