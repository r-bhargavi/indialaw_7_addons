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


class jasper_mis_report(JasperDataParser.JasperDataParser):
        
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_mis_report, self).__init__(cr, uid, ids, data, context)
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
        result = []
        self.sheet_names.append('MIS')
        proceed_pool = self.pool.get('court.proceedings')
        case_pool = self.pool.get('case.sheet')
        if data['form']['court_proceed_lines']:
            for proceed_obj in proceed_pool.browse(cr, uid, data['form']['court_proceed_lines'], context=context):
                next_date = False
                if proceed_obj.next_proceed_date:
                    next_date = dt.strptime(str(proceed_obj.next_proceed_date), '%Y-%m-%d').strftime('%d/%m/%Y')
                data = {
                    'sl_no': 0,
                    'file_no': proceed_obj.case_id.name,
                    'date_assign': dt.strptime(str(proceed_obj.case_id.date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                    'csm': proceed_obj.case_id.client_service_manager_id and proceed_obj.case_id.client_service_manager_id.name,
                    'office': proceed_obj.case_id.ho_branch_id.name,
                    'client': proceed_obj.case_id.client_id.name,
                    'client_ref': proceed_obj.case_id.company_ref_no,
                    'contact_per': proceed_obj.case_id.contact_partner1_id and proceed_obj.case_id.contact_partner1_id.name,
                    'contact_no': proceed_obj.case_id.contact_partner1_id and proceed_obj.case_id.contact_partner1_id.phone,
                    'email': proceed_obj.case_id.contact_partner1_id and proceed_obj.case_id.contact_partner1_id.email,
                    'ho_pi': '',
                    'team_head': proceed_obj.case_id.division_id.manager_id and proceed_obj.case_id.division_id.manager_id.name or '',
                    'type_work': case_pool.get_selection_value(cr, uid, 'work_type' , proceed_obj.case_id.work_type).encode('utf8', 'ignore'),
                    'case_no': proceed_obj.case_id.reg_number,
                    'complainant': proceed_obj.case_id.first_party,
                    'respondent': proceed_obj.case_id.opposite_party,
                    'court': proceed_obj.case_id.court_id.name,
                    'location': proceed_obj.case_id.court_location_id.name,
                    'district': proceed_obj.case_id.district_id and proceed_obj.case_id.district_id.name or False,
                    'state': proceed_obj.case_id.state_id.name,
                    'assignee': proceed_obj.case_id.assignee_id.name,
                    'mob_no': proceed_obj.case_id.assignee_id.mobile_phone,
                    'email_id': proceed_obj.case_id.assignee_id.work_email,
                    'proceed_date': dt.strptime(str(proceed_obj.proceed_date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                    'proceed_date_1': dt.strptime(str(proceed_obj.proceed_date), '%Y-%m-%d'),
                    'next_date': next_date,
                    'stage': proceed_obj.stage_id and proceed_obj.stage_id.name or '',
                    'last_proceed': proceed_obj.name,
                    }
                result.append(data)
            if result:
                result = sorted(result, key=itemgetter('file_no', 'proceed_date_1'))
#                 file_no = []
                i = 0
                for res in result:
                    i += 1
                    res.update({'sl_no': i})
#                     if res['file_no_1'] not in res:
#                         file_no.append(res['file_no_1'])
#                         res.update({'file_no': res['file_no_1']})
                    
        return result

jasper_report.report_jasper('report.jasper_mis_report', 'court.proceedings', parser=jasper_mis_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
