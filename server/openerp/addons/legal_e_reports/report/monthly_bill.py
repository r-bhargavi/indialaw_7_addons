# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2016 BroadTech Solutions Ltd.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import time
from datetime import datetime as dt
from operator import itemgetter

from legal_e_reports import JasperDataParser
from jasper_reports import jasper_report

from osv import fields, osv



class jasper_monthly_bill_report(JasperDataParser.JasperDataParser):
        
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_monthly_bill_report, self).__init__(cr, uid, ids, data, context)
        self.sheet_names=[]
        
    def generate_data_source(self, cr, uid, ids, data, context):
        return 'records'

    
    def generate_parameters(self, cr, uid, ids, data, context):
        if data['report_type']=='xls':
            return {'IS_IGNORE_PAGINATION':True}
        return {}

    def generate_properties(self, cr, uid, ids, data, context):
        return {
            'net.sf.jasperreports.export.xls.one.page.per.sheet':'true',
            'net.sf.jasperreports.export.xls.sheet.names.all': '/'.join(self.sheet_names),
            'net.sf.jasperreports.export.ignore.page.margins':'true',
            'net.sf.jasperreports.export.xls.remove.empty.space.between.rows':'true',
            'net.sf.jasperreports.export.xls.remove.empty.space.between.columns': 'true',
            'net.sf.jasperreports.export.xls.detect.cell.type': 'true',
            'net.sf.jasperreports.export.xls.white.page.background': 'false',
            'net.sf.jasperreports.export.xls.show.gridlines': 'true',
            'net.sf.jasperreports.export.xls.column.width': '10',
            'net.sf.jasperreports.export.xls.column.width.ratio': '1.0',
            }
        
    def generate_records(self, cr, uid, ids, data, context):
        result = [{'name': 'RRRRRRRRRRR'}]
        self.sheet_names.append('Monthly Bill')
        proceed_pool = self.pool.get('court.proceedings')
        case_pool = self.pool.get('case.sheet')
        account_pool = self.pool.get('account.account')
        move_pool = self.pool.get('account.move.line')
        domain = [('date', '>=', data['form']['date_from']), ('date', '<=', data['form']['date_to'])]
        if 'ho_branch_id' in data['form']:
            domain.append(('ho_branch_id', '=', data['form']['ho_branch_id'][0]))
        if 'state_id' in data['form']:
            domain.append(('state_id', '=', data['form']['state_id'][0]))
        
        if 'client_service_manager_id' in data['form']:
            domain.append(('client_service_manager_id', '=', data['form']['client_service_manager_id'][0]))
        
        case_ids = case_pool.search(cr, uid, domain, context=context)
        print '>>>>>>>>>>>>>>>>>>>>>>>>..',case_ids
        
        
        
        return result
    

jasper_report.report_jasper('report.jasper_monthly_bill', 'legal.monthly.bill', parser=jasper_monthly_bill_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
