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


office_ids = [
# Maharashtra
  87, # | Beed                  | BI
  17, # | Chembur               | LL
 103, # | Jalgaon               | JG
   2, # | Mumbai                | BOM
   1, # | PI_HO                 | PI_HO
  81, # | Pune                  | PU
# Kerala
  77, # | Alappuzha             | AL
  45, # | Cochin                | COK
  82, # | Kannur                | KNR
  55, # | Kollam                | KL
  76, # | Kottayam              | KT
  54, # | Kozhikode             | CCJ
  97, # | Malappuram            | MA
  79, # | Palakkad              | PL
  85, # | Pathanamthitta        | PT
  53, # | Thiruvanathapuram     | TV
 102, # | Thrissur              | TS
# Karnataka
  23, # | Bangalore             | BLR
  88, # | Dakshina Kannada      | DK
 107, # | Dharwad               | DH
# Tamil Nadu
  44, # | Chennai               | CHN
  93, # | Coimbatore            | CJB
 108, # | Madurai               | MA
  84, # | Salem                 | SA
# Telangana
 58, # | Adilabad               | ADB
 46, # | Hyderabad              | HYD
 62, # | Karimnagar             | KRM
 63, # | Khammam                | KHM
 65, # | Mahabubnagar           | MBN
 66, # | Nalgonda               | NLG
 67, # | Nizamabad              | NZB
 80, # | Ranga Reddy            | RR
 47, # | Warangal               | WGL
# Andhra Pradesh
 59, # | Anantapur              | ATP
 68, # | Chittoor               | CTR
 60, # | Cudappah               | CDP
 69, # | East Godavari          | EG
 70, # | Guntur                 | GTR
 71, # | Krishna                | KRI
 64, # | Kurnool                | KNL
 72, # | Nellore                | NLR
 73, # | Prakasam               | PKS
 95, # | Srikakulam             | SRI
 74, # | Vishakhapatnam         | VSP
 90, # | Vizianagaram           | VZM
 75, # | West Godavari          | WG
# Delhi
  6, # | Delhi | DL
# Gujarat
  56, # | Ahmedabad             | AMD
  94, # | Kheda                 | KHD
  57, # | Kutch                 | KTH
 104, # | Mehsana               | MA
  86, # | Sabarkantha           | SK
  91, # | Surat                 | STV
  83, # | Vadodara              | BRC
# West Bengal
  48, # | Kolkata               | KOA
# Bihar
 100, # | Patna                 | PA
# Uttarakhand
  98, # | Dehradun              | DD
# Haryana
 101, # | Panchkula             | PK
# Uttar Pradesh
 110, # | Kanpur                | KN
# Rajasthan
  99, # | Bhilwara              | BW
 109, # | Jodhpur               | JO
# Punjab
 105, # | Jalandhar             | JA
# Dubai
 36, # | Dubai                  | DXB
]


office_vals = {
    87 :  'beed',
    17 :  'chembur',
    103 :  'jalgaon',
    2 :  'mumbai',
    1 :  'pi_ho',
    81 :  'pune',
    77 :  'alappuzha',
    45 :  'cochin',
    82 :  'kannur',
    55 :  'kollam',
    76 :  'kottayam',
    54 :  'kozhikode',
    97 :  'malappuram',
    79 :  'palakkad',
    85 :  'pathanamthitta',
    53 :  'trivandrum',
    102 :  'thrissur',
    23 :  'bangalore',
    88 :  'dakshina',
    107 :  'dharwad',
    44 :  'chennai',
    93 :  'coimbatore',
    108 :  'madurai',
    84 :  'salem',
    58 :  'adilabad',
    46 :  'hyderabad',
    62 :  'karimnagar',
    63 :  'khammam',
    65 :  'mahabubnagar',
    66 :  'nalgonda',
    67 :  'nizamabad',
    80 :  'ranga',
    47 :  'warangal',
    59 :  'anantapur',
    68 :  'chittoor',
    60 :  'cudappah',
    69 :  'east_godavari',
    70 :  'guntur',
    71 :  'krishna',
    64 :  'kurnool',
    72 :  'nellore',
    73 :  'prakasam',
    95 :  'srikakulam',
    74 :  'vishakhapatnam',
    90 :  'vizianagaram',
    75 :  'west_godavari',
    6 :  'delhi',
    56 :  'ahmedabad',
    94 :  'kheda',
    57 :  'kutch',
    104 :  'mehsana',
    86 :  'sabarkantha',
    91 :  'surat',
    83 :  'vadodara',
    48 :  'kolkata',
    100 :  'patna',
    98 :  'dehradun',
    101 :  'panchkula',
    110 :  'kanpur',
    99 :  'bhilwara',
    109 :  'jodhpur',
    105 :  'jalandhar',
    36 :  'dubai'
    }


class jasper_cost_report(JasperDataParser.JasperDataParser):
        
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_cost_report, self).__init__(cr, uid, ids, data, context)
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
        self.sheet_names.append('Cost')
        proceed_pool = self.pool.get('court.proceedings')
        case_pool = self.pool.get('case.sheet')
        account_pool = self.pool.get('account.account')
        move_pool = self.pool.get('account.move.line')
        
        
        company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        account_ids = [acount_obj.id for cost_obj in company_obj.cost_report_ids for acount_obj  in cost_obj.account_ids]
        
        account_details = {}
        account_ids = []
        for cost_obj in company_obj.cost_report_ids:
            mapped_accts = []
            for acount_obj in cost_obj.account_ids:
                mapped_accts.append(acount_obj.id)
            account_details.update({cost_obj.name : [cost_obj.sequence , mapped_accts]})
            account_ids += mapped_accts
        
        cr.execute("""
        select 
        al.name, al.office_id, al.account_id, al.debit ,aa.name, aa.code
        from account_move_line as al 
        left join account_account as aa on (aa.id=al.account_id)
        where al.account_id in %s and al.office_id in %s and al.debit is not null and al.period_id = %s
        
        ;"""
        ,(tuple(account_ids),tuple(office_vals.keys()),data['form']['period_id'][0],))
        expense = map(lambda x: x, cr.fetchall())
        for rows in expense:
            vals = {
                'name': rows[0],
                'account_id': rows[2],
                'account_name': '['+ rows[5] + '] '+ rows[4],
                }
            for key in account_details.keys():
                if rows[2] in  account_details[key][1]:
                    vals.update({'head_name': key, 'sequence': account_details[key][0]})
                    
            vals.update({office_vals[rows[1]]: rows[3]})
            result.append(vals)
            
        res_data = []
        if result:
            
            data = {}
            for res in result:
                if ((res['head_name'], res['account_id'], res['sequence'], res['account_name'])) in data:
                    for value in office_vals.values():
                        if value in res:
                            if value in data[(res['head_name'], res['account_id'], res['sequence'], res['account_name'])]:
                                data[(res['head_name'], res['account_id'], res['sequence'], res['account_name'])][value] += res[value]
                            else:
                                data[(res['head_name'], res['account_id'], res['sequence'], res['account_name'])][value] = res[value]
                    
                else:
                    data[(res['head_name'], res['account_id'], res['sequence'], res['account_name'])] = {}
                    for value in office_vals.values():
                        if value in res:
                            data[(res['head_name'], res['account_id'], res['sequence'], res['account_name'])][value] = res[value]
                            
            
            for key in data.keys():
                res_vals = {
                    'head_name': key[0],
                    'account_id': key[1],
                    'sequence': key[2],
                    'account_name': key[3],
                    }
                
                for value in data[key].keys():
                    res_vals.update({value: data[key][value]})
                res_data.append(res_vals)
            
        if res_data:
            res_data = sorted(res_data, key=itemgetter('sequence', 'account_id'))
        return res_data
    

jasper_report.report_jasper('report.jasper_cost_report', 'legal.cost.sheet', parser=jasper_cost_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
