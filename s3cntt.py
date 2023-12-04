import re
text="""
TAX INVOICE [1 Original for ecepient —_] Triplicate for supplier
1 Duplicate for transporter C1] Extra copy
Invoice No. : Date :
BULZER TECH 7468/23-24 24112023
Plot No:14/A,Survey No.157/4,Ground, Ist, 2nd & 3rd Floor, Purchase Order No. : Date :       
Wahab Nagar Co-Operative Housing Society Limited, Near
Diamond Point Circle, Thokatta Vill Secunderabad 500009 Payment tenn Dustales
STATE :36 - TELANGANA ERENT DATE i
PHONE NO.:040-27900000,29310000 24/11/2023
GSTIN:36AAOPL8099C1Z8 PAN: AAOPL8099C Agent's Ref. : DC No. :
TAN: HYDP02035F cTc
BUYER'S NAME AND ADDRESS:
C PROMPT SOLUTIONS PRIVATE LIMITED
BALDWA EDIFICE 2-4-438,441 IRN
3RD FLOOR RAMGOPALPET ROAD 23082986598c7dc210b12dfd78c3a
Sevunderabsd..500003 £8849d0073776609481 0564438658
124a0a6
STATE : 36 - TELANGANA “
CONTACT PERSON : ADITYA
PHONE NO.: 97004 87282
GSTIN :36AAKCC1867C1ZQ PAN: AAKCC1867C
Remarks
sl. inti HSN | aty Rate cest | scst Iest Taxable
Product Description Code | (Nos) | _Rs. Tax Tax Tax Value
1 | DELLOPTIPLEX 7010 MT is 13500 8/1TB+256 84714900] 39 38,983.05 13683051) 136830.51 1,820,338 99
SSD DOS 3 YRS
DY.5VX3:69MSVX3;7WLBVXG.H TMEVXS;77MBVX3.9 7MSVX3,68MBVX (9.00%) | (@.00%)
19MSVX3:HEMSVXG, 37M5VX3:P1.5VX3,C8MSVXG, ML SVKS;DBMSVX
5, FOMSVX3,57 MSVX3: 49MSVXS:G8MSVK3,F7MSVX3,5WLSVKS-47MSVX
3 HOMBVX3,DTMGVXG,7MSVXS,CEMOVXS: 20M SVKS.48MSVIG,6M5V
X3,79MBVX3:D66 5VX3J8M5VX3,67M SVX, 86M5VXG,F6MSVX3;10MSV
X3,B6MSUKS,27 MSVIG,J6MSVIG,72MBVX3
2 | RAM 8GB DDR4 84733099] 15 127119) 171610) 1716.10 19,067.79
(9.00%) | (9.00%)
FREIGHT 9,750.00)
TOTAL TAXABLE AMOUNT 1,549,156.78)
CGST 9.000% 139,424.11
SGST 9.000% 139,424.11
TOTAL QTY: 54 GRAND TOTAL: 1,828,005.00
[AMOUNT IN WORDS: RUPEES EIGHTEEN LAKHS TWENTY-EIGHT THOUSAND FIVE ONLY.
TERM AND CONDITIONS : BANK DETAIL
1. NO WARRANTY FOR BURNT/PHYSICAL DAMAGE. Bank —: INDUSIND BANK
2. Goods once sold will not be taken back or exchanged. Branch : $.P.ROAD,BEGUMPET
3. All disputes are subjected to HYDERABAD Jurisdiction Alc No. :650014134745
4, Incase of default in payment BULZER TECH will have all the rights to repossess the goods. IFSC -INDBO000004
8. In case cheque is dishonoured RS.500/- will be charged and 24% Interest will be charged.  
6. Responsibility of warranty lies with the manufacturer only. ‘Transport Mode
7. Customer Declaration: | have accepted the above mentioned conditions and taken delivery Carrier Name
only after verifying the above. Waybill No



BULZER -040-27900000
DELL -18004250088
GODREJ -18002095511
SONY = -18001037799
HP +18002587170



Receiver's Signature with stamp

E.80.E
For BULZER TECH

"""

import datetime
import re
from collections import namedtuple

pattern = r"(?:(?:\d+\s*[^\d\s]*\s*)*)(?P<inv_date>\d{6}).+(?P<due_date>\d{6}).+?(?P<inv_amt>[\d,]+\.\d{2}).+?(?P<net_amt>[\d,]+\.\d{2})(?P<description>.*)"
vend_pattern = "^(?P<vend_num>\d{3})\s(?P<vend_name>[A-Za-z0-9/,\s&\.()]+)$"
Invoice = namedtuple('Invoice', 'vend_num vend_name inv_date due_date inv_amt net_amt description')

data_list = []
vend_num = vend_name = None

for line in text:
    vend_line = re.search(vend_pattern, line)
    if vend_line:
        vend_num = vend_line.group('vend_num')
        vend_name = vend_line.group('vend_name')
        continue
    match = re.search(pattern, line)
    if match:
        inv_date = datetime.datetime.strptime(match.group('inv_date'), "%m%d%y")
        due_date = datetime.datetime.strptime(match.group('due_date'), "%m%d%y")
        inv_amt = float(match.group('inv_amt').replace(',', ''))
        net_amt = float(match.group('net_amt').replace(',', ''))
        description = match.group('description')
        invoice = Invoice(vend_num, vend_name, inv_date=inv_date, due_date=due_date, inv_amt=inv_amt, net_amt=net_amt, description=description)
        data_list.append(invoice)

# Printing the collected data (for demonstration purposes)
for invoice in data_list:
    print(invoice)
