import os
from fpdf import FPDF

sample_dir = os.path.join(os.path.dirname(__file__), "sample_documents")
os.makedirs(sample_dir, exist_ok=True)

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(180, 10, 'CYBER CRIME POLICE STATION - HYDERABAD', new_x='LMARGIN', new_y='NEXT', align='C')
pdf.set_font('Helvetica', '', 10)
pdf.cell(180, 6, 'FIRST INFORMATION REPORT (U/S 154 Cr.P.C.)', new_x='LMARGIN', new_y='NEXT', align='C')
pdf.cell(180, 6, 'CONFIDENTIAL INVESTIGATION DOSSIER - SPECIAL INVESTIGATION UNIT', new_x='LMARGIN', new_y='NEXT', align='C')
pdf.ln(5)

fir_text = """1. DISTRICT: Hyderabad City Commissionerate
2. POLICE STATION: Cyber Crime PS, Cyberabad
3. FIR NO: FIR-2026-014 | DATE: 2026-09-10 | TIME: 09:30 hrs
4. ACTS & SECTIONS: Section 420, 120-B IPC & Section 66D IT Act 2000

5. SUSPECTS / PERSONS IDENTIFIED:
- Accused 1: Rahul Kumar, residing at Banjara Hills, Hyderabad. Contact mobile: 9876543210.
  Bank account identified: ACC001 (HDFC Bank).
- Accused 2: Arjun Singh, operating from Hitech City, Hyderabad. Contact mobile: 9123456789.
  Bank account identified: ACC002 (ICICI Bank).
- Accused 3: Ravi Sharma, facilitator, residing in Hyderabad. Contact mobile: 9988776655.
  Bank account identified: ACC003 (Axis Bank).
- Key Corporate Front: Apex Traders Pvt Ltd, registered office at Hitech City.

6. STATEMENT OF FACTS & EVIDENCE:
On 2026-09-10 at 10:30 hrs, surveillance intercepted telecommunication activity between mobile number 9876543210 (Rahul Kumar) and 9123456789 (Arjun Singh), recording a call duration of 120 seconds.

Subsequent intelligence revealed that at 12:00 hrs, Rahul Kumar placed a secondary phone call to Ravi Sharma on 9988776655 for 60 seconds discussing financial logistics.

Financial ledger scrutiny indicates that at 12:45 hrs on 2026-09-10, an electronic fund transfer of INR 50,000 was executed from account ACC001 (Rahul Kumar) into account ACC002 (Arjun Singh).

Following this initial transfer, at 13:10 hrs on the same day, a secondary transfer of INR 25,000 was dispatched from account ACC001 into account ACC003 belonging to Ravi Sharma.

At 15:30 hrs, account ACC002 transferred INR 10,000 into account ACC003. Shortly thereafter at 16:00 hrs, account ACC003 remitted a kickback transfer of INR 5,000 back into account ACC001, completing a suspicious circular money trail.

Field units also reported vehicle TS 09 AB 1234 registered to Rahul Kumar spotted outside the office of Apex Traders Pvt Ltd in Hitech City at 14:00 hrs.

Further investigation into the criminal network and related accounts is ongoing under Case Reference CASE-2026-014.
"""

pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(180, 5, fir_text)

pdf_path = os.path.join(sample_dir, "FIR_Case_2026_014.pdf")
pdf.output(pdf_path)
print(f"Generated PDF: {pdf_path}")

# 2. Create Surveillance Log Text Document
surv_text = """INVESTIGATION SURVEILLANCE LOG - CASE-2026-014
DATE: 2026-09-11
INVESTIGATING UNIT: Special Surveillance Wing

08:15 hrs - Suspect Rahul Kumar observed exiting residence at Banjara Hills in vehicle TS 09 AB 1234.
09:20 hrs - Rahul Kumar met associate Vikram Malhotra near Jubilee Hills coffee house.
10:45 hrs - Rahul Kumar placed phone call to 9123456789 (Arjun Singh). Call duration 180 seconds.
11:30 hrs - Arjun Singh arrived at Hitech City Commercial Complex driving MH 01 CD 5678.
13:15 hrs - Arjun Singh visited Global Financial Ltd premises in Hitech City.
14:30 hrs - Ravi Sharma spotted receiving an envelope from an unknown courier near Secunderabad Station.
16:00 hrs - Electronic fund transfer detected: INR 75,000 routed through shell account AC-981245.
17:45 hrs - Intercepted message indicates planned movement of documents to Airport Cargo Terminal tomorrow.
"""

surv_path = os.path.join(sample_dir, "Surveillance_Log_Field_Report.txt")
with open(surv_path, "w", encoding="utf-8") as f:
    f.write(surv_text)
print(f"Generated TXT: {surv_path}")

# 3. Create Bank Transactions Log
bank_text = """sender_account,receiver_account,date,time,amount
ACC001,ACC002,2026-09-10,12:45,50000
ACC001,ACC003,2026-09-10,13:10,25000
ACC002,ACC003,2026-09-10,15:30,10000
ACC003,ACC001,2026-09-10,16:00,5000
ACC002,ACC004,2026-09-11,09:15,35000
"""
bank_path = os.path.join(sample_dir, "Bank_Transactions_Audit.csv")
with open(bank_path, "w", encoding="utf-8") as f:
    f.write(bank_text)
print(f"Generated CSV: {bank_path}")
