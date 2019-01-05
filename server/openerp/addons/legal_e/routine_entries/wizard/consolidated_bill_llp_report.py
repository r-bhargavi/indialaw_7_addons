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
from openerp.tools.amount_to_text_en import amount_to_text


class consolidated_bill_llp(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(consolidated_bill_llp, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'get_amt_inwords':self.get_amt_inwords,
            'get_date':self.get_date,
            'get_lines':self.get_lines,
        })
    
    def get_lines(self, lines):
        res = []
        sl_no = 0
        for line in lines:
            sl_no = sl_no+1
            data = {'sl_no':sl_no,'name':line.name,'amount':line.amount}
            res.append(data)
        for i in range(1,21):
            res.append({'sl_no':'','name':'','amount':''})
        return res
    
    def get_amt_inwords(self, invoice, total,ttype,currency_id):
        if ttype == 'words':
            amt_in_words = amount_to_text(total,'en',currency_id.name)
            if currency_id.name == 'INR':
                amt_in_words = amt_in_words.replace('INR','Rupees').replace('Cents','Paisa').replace('Cent','Paisa')
                return amt_in_words
        else:
            return total
        
    def get_date(self, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dt = datetime.strftime(dt, "%d-%b-%y")
        return dt
report_sxw.report_sxw('report.consolidated.bill.llp', 'consolidated.bill', 'addons/legal_e/routine_entries/wizard/consolidated_bill_llp_report.rml', parser=consolidated_bill_llp, header=False)
report_sxw.report_sxw('report.consolidated.bill.hdfc', 'consolidated.bill', 'addons/legal_e/routine_entries/wizard/consolidated_bill_hdfc_report.rml', parser=consolidated_bill_llp, header=False)
report_sxw.report_sxw('report.consolidated.bill.cbi', 'consolidated.bill', 'addons/legal_e/routine_entries/wizard/consolidated_bill_cbi_report.rml', parser=consolidated_bill_llp, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: