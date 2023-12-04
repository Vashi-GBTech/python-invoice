 

text="""TAX INVOICE [1 Original for ecepient —_] Triplicate for supplier
1 Duplicate for transporter C1] Extra copy
Invoice No. : Date :
BULZER TECH 7468/23-24 2411112023
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
HP +18002587170"""


# import re
# pattern1= r'\bGRAND TOTAL:.*\d(?:\.\d+)?\b'
# pattern2 = r'^Total.*?\d{1,3}(?:,\d{3})*\.\d{2}$'
# pattern=pattern1+pattern2
# matches = re.findall(pattern, text)
# if matches:
#     for match in matches:
#         print(match)
# else:
#     print("No match found.") 
 
 


import re

text = "Invoice No. : Date : BULZER TECH 7468/23-24 2411112023"

# Regex pattern to extract the Invoice Number and Date
invoice_number_pattern = r'(?<=Invoice No\. : )(\S+)'
date_pattern = r'(?<=Date : )(\d{8})'

# Find Invoice Number and Date using regex
invoice_number_match = re.search(invoice_number_pattern, text)
date_match = re.search(date_pattern, text)

if invoice_number_match:
    invoice_number = invoice_number_match.group(1)
    print("Invoice Number:", invoice_number)
else:
    print("Invoice Number not found.")

if date_match:
    date = date_match.group(1)
    # Assuming the date is in the format ddmmyyyy, for example, 24112023 (24th November 2023)
    formatted_date = f"{date[0:2]}/{date[2:4]}/{date[4:]}"
    print("Date:", formatted_date)
else:
    print("Date not found.")
