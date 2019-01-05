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
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.report import report_sxw

class voucher_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(voucher_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'get_amt_inwords':self.get_amt_inwords,
            'get_date':self.get_date,
            'get_lines':self.get_lines,
            'get_lines_cost': self.get_lines_cost,
        })
    
    def get_lines(self, lines):
        res = []
        sl_no = 0
        debit = []
        credit = []
        for line in lines:
            sl_no = sl_no+1
            vals = {
                'sl_no':sl_no,
                'name':line.name,
                'purpose': '',
                'account_id': line.account_id.code + ' ' + line.account_id.name,
                'case_id': line.case_id.name,
                'office_id': line.office_id.name,
                'dept_id': line.department_id.name,
                'debit': line.debit,
                'credit': 0.0,
                'sequence': 1
                 }
            if line.debit:
                vals.update({'debit': line.debit})
            else:
                vals.update({'credit':line.credit,'sequence' : 1000})
            res.append(vals)
        res =  sorted(res, key = lambda user: (user['sequence']))
        return res
    
    def get_lines_cost(self, lines):
        res = []
        sl_no = 0
        for line in lines:
            sl_no = sl_no+1
            # Change amount as price_unit // Sanal Davis // 12-6-15 
            data = {'sl_no':sl_no,'name':line.name,'amount':line.price_subtotal}
            res.append(data)
        for i in range(1,21):
            res.append({'sl_no':'','name':'','amount':''})
        return res
    
    def get_amt_inwords(self, invoice, total,ttype):
        
        if ttype == 'words':
            amt_in_words = amount_to_text(total,'en',invoice.currency_id.name)
            if invoice.currency_id.name == 'INR':
                amt_in_words = amt_in_words.replace('INR','Rupees').replace('Cents','Paisa').replace('Cent','Paisa')
                return amt_in_words
        else:
            return total
        
    def get_date(self, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dt = datetime.strftime(dt, "%d-%b-%y")
        return dt
        
        

report_sxw.report_sxw('report.legale.account.move', 'account.move', 'addons/legal_e_reports/report/voucher_print.rml', parser=voucher_print, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: