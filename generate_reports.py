from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

OUT = r'd:\astrava\samples'

RED   = colors.HexColor('#c0392b')
ORG   = colors.HexColor('#e67e22')
NAVY  = colors.HexColor('#1a2e4a')
LGRAY = colors.HexColor('#f7f9fc')
DGRAY = colors.HexColor('#2c3e50')
WHITE = colors.white

def build_pdf(filename, title, report_id, patient, age, gender, date,
              vitals, complaint, history, symptoms, exam, labs,
              impression, plan, risk_label, risk_color):
    path = os.path.join(OUT, filename)
    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    hl = '<font color="white" size="15"><b>MEDICAL REPORT</b></font>'
    hr_sub = '<font color="#aed6f1" size="8">' + title + '</font>'
    hrr = '<font color="white" size="8"><b>Report ID:</b> ' + report_id + '<br/><b>Date:</b> ' + date + '</font>'
    header_data = [[
        Paragraph(hl + '<br/>' + hr_sub, styles['Normal']),
        Paragraph(hrr, ParagraphStyle('rh', alignment=TA_RIGHT, fontName='Helvetica', fontSize=8))
    ]]
    ht = Table(header_data, colWidths=[12*cm, 5.5*cm])
    ht.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), NAVY),
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('PADDING', (0,0),(-1,-1), 10),
    ]))
    story.append(ht)
    story.append(Spacer(1, 0.4*cm))

    # Patient info
    info_style = ParagraphStyle('inf', fontName='Helvetica', fontSize=9, textColor=DGRAY)
    pi = Table([[
        Paragraph('<b>Patient:</b>  ' + patient, info_style),
        Paragraph('<b>Age:</b>  ' + age + '  |  <b>Gender:</b>  ' + gender, info_style),
    ]], colWidths=[9*cm, 8.5*cm])
    pi.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), LGRAY),
        ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#dce6f1')),
        ('PADDING',(0,0),(-1,-1),8),
    ]))
    story.append(pi)
    story.append(Spacer(1, 0.4*cm))

    # Risk badge
    rb_text = '<font color="white" size="11"><b>RISK ASSESSMENT: ' + risk_label + '</b></font>'
    rb = Table([[Paragraph(rb_text, ParagraphStyle('rb', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11))]],
               colWidths=[17.5*cm])
    rb.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), risk_color),
        ('PADDING',(0,0),(-1,-1),8),
    ]))
    story.append(rb)
    story.append(Spacer(1, 0.4*cm))

    def section(title_text, items):
        story.append(Paragraph(
            '<font color="#1a2e4a" size="10"><b>' + title_text + '</b></font>',
            ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=10,
                           textColor=NAVY, spaceAfter=3)))
        story.append(HRFlowable(width='100%', thickness=0.8, color=NAVY, spaceAfter=4))
        body = ParagraphStyle('body', fontName='Helvetica', fontSize=9,
                              textColor=DGRAY, leading=14, leftIndent=10)
        for item in items:
            story.append(Paragraph(item, body))
        story.append(Spacer(1, 0.35*cm))

    def vital_table(rows):
        tdata = [[
            Paragraph('<b>' + k + '</b>',
                      ParagraphStyle('vk', fontName='Helvetica-Bold', fontSize=9, textColor=NAVY)),
            Paragraph(v, ParagraphStyle('vv', fontName='Helvetica', fontSize=9, textColor=DGRAY))
        ] for k,v in rows]
        t = Table(tdata, colWidths=[6.5*cm, 11*cm])
        t.setStyle(TableStyle([
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[LGRAY, WHITE]),
            ('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#dce6f1')),
            ('INNERGRID',(0,0),(-1,-1),0.2,colors.HexColor('#dce6f1')),
            ('PADDING',(0,0),(-1,-1),5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        '<font color="#1a2e4a" size="10"><b>VITAL SIGNS</b></font>',
        ParagraphStyle('sh2', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY, spaceAfter=3)))
    story.append(HRFlowable(width='100%', thickness=0.8, color=NAVY, spaceAfter=4))
    vital_table(vitals)

    section('CHIEF COMPLAINT', [complaint])
    section('MEDICAL HISTORY', history)
    section('CURRENT SYMPTOMS', symptoms)
    section('PHYSICAL EXAMINATION', exam)
    section('LABORATORY / DIAGNOSTIC FINDINGS', labs)
    section('CLINICAL IMPRESSION', [impression])
    section('TREATMENT PLAN', plan)

    story.append(HRFlowable(width='100%', thickness=0.5,
                            color=colors.HexColor('#bdc3c7'), spaceAfter=4))
    story.append(Paragraph(
        '<font size="7" color="#7f8c8d">This report is generated for the AI Medical Report Interpreter platform. '
        'Always consult a licensed physician before acting on any medical information.</font>',
        ParagraphStyle('foot', alignment=TA_CENTER, fontName='Helvetica',
                       fontSize=7, textColor=colors.HexColor('#7f8c8d'))))

    doc.build(story)
    print('Created:', path)


# ========== REPORT 1 — HIGH RISK: Hypertensive Crisis + Cardiac ==========
build_pdf(
    filename='report_high_risk_cardiac.pdf',
    title='Hypertensive Crisis with Acute Cardiac Decompensation',
    report_id='MR-2026-H001',
    patient='Rajesh Kumar',
    age='54 years',
    gender='Male',
    date='March 7, 2026',
    vitals=[
        ('Blood Pressure',    '195/125 mmHg  [CRITICAL]'),
        ('Temperature',       '103.8 F (39.9 C)  [HIGH FEVER]'),
        ('Heart Rate',        '118 bpm  [Tachycardia]'),
        ('Respiratory Rate',  '26 breaths/min  [Elevated]'),
        ('SpO2',              '91% on room air  [Hypoxemia]'),
        ('Blood Glucose',     '320 mg/dL  [Hyperglycemia]'),
        ('Weight / BMI',      '88 kg  |  BMI: 31.4 (Obese Class I)'),
    ],
    complaint=(
        'Patient presents to emergency with severe crushing chest pain (8/10), sudden-onset severe '
        'headache, blurred vision, and new-onset confusion lasting 4 hours. '
        'Associated palpitations and progressive shortness of breath at rest.'
    ),
    history=[
        '- Hypertension: diagnosed 6 years ago, irregular medication compliance',
        '- Type 2 Diabetes Mellitus: on metformin and glipizide',
        '- Ischaemic Heart Disease: drug-eluting stent to LAD 3 years ago',
        '- Dyslipidaemia: on atorvastatin 40mg',
        '- Father died of acute MI at age 58 — strong family history',
        '- Smoker: 1 pack/day x 25 years  |  Occasional alcohol',
    ],
    symptoms=[
        '- Crushing central chest pain radiating to left arm and jaw',
        '- Severe headache — "worst of my life" (possible hypertensive encephalopathy)',
        '- Blurred and double vision',
        '- Acute confusion and disorientation x 4 hours',
        '- Palpitations: irregular rhythm noted by patient',
        '- Profuse diaphoresis, cold clammy skin',
        '- Progressive dyspnoea: unable to walk 10 metres without stopping',
        '- Bilateral lower-limb oedema (pitting, up to knee level)',
        '- Nocturia x4/night over past 2 weeks',
    ],
    exam=[
        '- General: Acutely unwell, diaphoretic, pale, confused (GCS 14/15)',
        '- CVS: S1 S2 + S3 gallop; elevated JVP; apex beat displaced laterally to 6th ICS AAL',
        '- Respiratory: Bibasal fine crepitations — early pulmonary oedema pattern',
        '- Fundoscopy: Grade III hypertensive retinopathy with flame haemorrhages',
        '- Abdomen: Mild hepatomegaly; bilateral renal bruits auscultated',
        '- Neurology: Confused; pupils equal and reactive; no focal neurological deficit',
        '- Lower limbs: 3+ pitting oedema bilateral; peripheral pulses present but weak',
    ],
    labs=[
        '- Troponin I: 0.84 ng/mL [ELEVATED — Normal <0.04] — NSTEMI likely',
        '- BNP: 820 pg/mL [ELEVATED — Normal <100] — Acute heart failure',
        '- HbA1c: 11.2% [POOR control — Target <7%]',
        '- Serum Creatinine: 2.1 mg/dL [ELEVATED] — Acute kidney injury',
        '- eGFR: 34 mL/min [CKD Stage 3b]',
        '- Serum Potassium: 5.8 mEq/L [Hyperkalaemia — CRITICAL]',
        '- WBC: 14,200/uL [Leucocytosis]  |  Hb: 10.8 g/dL [Anaemia]',
        '- Total Cholesterol: 268 mg/dL  |  LDL: 178 mg/dL [Elevated]',
        '- ECG: ST-depression V4-V6; LBBB pattern; Left ventricular hypertrophy',
        '- Chest X-Ray: Cardiomegaly; bilateral hilar haziness (pulmonary oedema)',
        '- Echo (bedside): LVEF 32% [Severely reduced — Normal >55%]',
    ],
    impression=(
        'Hypertensive emergency with acute decompensated heart failure (LVEF 32%). '
        'High suspicion of NSTEMI — troponin elevated with ECG changes. '
        'Acute kidney injury on background of diabetic nephropathy. '
        'Requires urgent CCU admission, cardiology review, and nephrology consult.'
    ),
    plan=[
        '1. IMMEDIATE: IV labetalol / nicardipine — target BP <160/100 within 1 hour',
        '2. Oxygen therapy — maintain SpO2 >= 94%; consider CPAP if not improving',
        '3. IV furosemide 80mg STAT for acute pulmonary oedema',
        '4. Serial troponin and ECG every 3 hours',
        '5. Insulin sliding scale infusion for hyperglycaemia',
        '6. Nephrology consult — monitor urine output hourly; avoid nephrotoxins',
        '7. Urgent coronary angiography if troponin trend rises',
        '8. Continuous cardiac telemetry monitoring',
        '9. Stop NSAIDs; review all potentially nephrotoxic medications',
        '10. Diabetes educator and cardiac rehab referral post-stabilisation',
    ],
    risk_label='HIGH RISK — CRITICAL — IMMEDIATE HOSPITALISATION REQUIRED',
    risk_color=RED,
)

# ========== REPORT 2 — HIGH RISK: Sepsis / Pneumonia ==========
build_pdf(
    filename='report_high_risk_sepsis.pdf',
    title='Severe Community-Acquired Pneumonia with Septic Shock',
    report_id='MR-2026-H002',
    patient='Priya Nair',
    age='67 years',
    gender='Female',
    date='March 7, 2026',
    vitals=[
        ('Blood Pressure',    '88/56 mmHg  [HYPOTENSION — Septic shock]'),
        ('Temperature',       '105.1 F (40.6 C)  [CRITICAL FEVER]'),
        ('Heart Rate',        '128 bpm  [Severe Tachycardia]'),
        ('Respiratory Rate',  '32 breaths/min  [Severe Tachypnoea]'),
        ('SpO2',              '84% on high-flow oxygen  [CRITICAL Hypoxaemia]'),
        ('GCS',               '11/15  [E3V3M5 — Altered consciousness]'),
        ('Weight',            '62 kg'),
    ],
    complaint=(
        'Brought by family with 6-day history of worsening productive cough (green sputum), '
        'high fever, and rapid deterioration in breathing over the past 18 hours. '
        'Patient unable to complete sentences; using accessory muscles to breathe. '
        'Family reports she became confused this morning.'
    ),
    history=[
        '- COPD: on tiotropium and salbutamol PRN — FEV1 58% predicted',
        '- Rheumatoid arthritis: on methotrexate 15mg/week (IMMUNOSUPPRESSED)',
        '- Hypertension: on amlodipine 5mg',
        '- Previous hospitalisation for pneumonia 2 years ago (same organism)',
        '- Non-smoker  |  No alcohol',
        '- Influenza vaccine: 2024  |  COVID vaccine: up to date',
    ],
    symptoms=[
        '- Productive cough: large amounts of green-yellow purulent sputum x6 days',
        '- High fever with severe rigors and drenching night sweats',
        '- Severe dyspnoea at rest: unable to walk to bathroom',
        '- Right-sided pleuritic chest pain worsening on inspiration',
        '- New-onset confusion: disoriented to time and place',
        '- Markedly reduced urine output for 24 hours',
        '- Nausea and vomiting x3 episodes yesterday',
        '- Poor oral intake x4 days: estimated <400 kcal/day',
        '- Central cyanosis noted by family',
    ],
    exam=[
        '- General: Acutely distressed, central cyanosis, using scalene and intercostal muscles',
        '- Respiratory: Dull percussion right base; bronchial breathing right lower zone; bilateral crackles',
        '- CVS: Tachycardic; BP critically low; cold peripheries; capillary refill 5 seconds',
        '- Abdomen: Mild RUQ tenderness; soft; no guarding or rigidity',
        '- Neurology: Confused; GCS 11; pupils equal reactive; no focal deficit',
        '- Skin: Mottled lower limbs; no petechiae or purpura',
        '- Tourniquet test: Negative',
    ],
    labs=[
        '- WBC: 24,600/uL [Severe leucocytosis]  |  Bands: 18% [CRITICAL]',
        '- CRP: 412 mg/L [Severe inflammation — Normal <5]',
        '- Procalcitonin: 28 ng/mL [High — bacterial sepsis confirmed]',
        '- Lactate: 4.8 mmol/L [CRITICAL — tissue hypoperfusion]',
        '- Blood cultures: x2 sets drawn before antibiotics — pending',
        '- Serum Creatinine: 2.8 mg/dL [Acute kidney injury — KDIGO Stage 2]',
        '- ALT: 135 U/L  |  AST: 178 U/L [Hepatic dysfunction]',
        '- ABG: pH 7.26 [Acidosis]  |  PaO2 52 mmHg  |  PaCO2 52 mmHg',
        '- Sputum MC+S: Gram-positive diplococci — Streptococcus pneumoniae presumed',
        '- Chest X-Ray: Dense right lower lobe consolidation + right-sided pleural effusion',
        '- CURB-65 Score: 4/5 — Severe CAP (mortality risk 27-40%)',
    ],
    impression=(
        'Severe Community-Acquired Pneumonia (right lower lobe, likely S. pneumoniae) '
        'progressing to septic shock with multi-organ dysfunction: acute kidney injury '
        'and hepatic involvement. Metabolic acidosis with respiratory component. '
        'High mortality risk. Possible empyema right side. '
        'Requires immediate ICU admission and Sepsis-6 bundle activation.'
    ),
    plan=[
        '1. IMMEDIATE ICU ADMISSION — activate Sepsis-6 protocol',
        '2. IV ceftriaxone 2g + azithromycin 500mg within 1 hour of admission',
        '3. IV fluid resuscitation: 30 mL/kg crystalloid — reassess after each bolus',
        '4. Noradrenaline vasopressor if MAP remains <65 mmHg after 2L fluid',
        '5. High-flow nasal cannula 40L/min; intubation criteria pre-set if SpO2 not maintained',
        '6. Urinary catheter — hourly urine output target 0.5 mL/kg/hr',
        '7. Respiratory physician + ID team review within 2 hours',
        '8. HOLD methotrexate during acute sepsis; haematology review',
        '9. Pleural ultrasound: chest drain if empyema confirmed on CT thorax',
        '10. DVT prophylaxis with enoxaparin when haemodynamically stable',
    ],
    risk_label='HIGH RISK — CRITICAL — ICU ADMISSION & SEPSIS PROTOCOL ACTIVATED',
    risk_color=RED,
)

# ========== REPORT 3 — MODERATE RISK: Dengue Fever ==========
build_pdf(
    filename='report_moderate_risk_dengue.pdf',
    title='Dengue Fever — Moderate Risk with Warning Signs',
    report_id='MR-2026-M001',
    patient='Suresh Pillai',
    age='29 years',
    gender='Male',
    date='March 7, 2026',
    vitals=[
        ('Blood Pressure',    '112/72 mmHg  (Adequate — monitor closely)'),
        ('Temperature',       '102.6 F (39.2 C)  — Fever Day 4'),
        ('Heart Rate',        '98 bpm  (Mild tachycardia for fever level)'),
        ('Respiratory Rate',  '18 breaths/min  (Normal)'),
        ('SpO2',              '98% on room air  (Normal)'),
        ('Weight / BMI',      '71 kg  |  BMI: 23.1'),
    ],
    complaint=(
        '4-day history of sudden-onset high fever, severe joint and muscle pain described '
        'as "bone-breaking" sensation, intense retro-orbital headache, and a rash appearing '
        'today (Day 4). Marked fatigue. Minor gum bleeding noticed this morning on brushing.'
    ),
    history=[
        '- No significant past medical history; no chronic medications',
        '- Lives in Bengaluru: dengue-endemic area; neighbour recently hospitalised for dengue',
        '- Travelled to rural Karnataka 2 weeks ago (possible exposure)',
        '- No dengue vaccination history',
        '- Non-smoker  |  Occasional alcohol',
        '- No known allergies',
    ],
    symptoms=[
        '- High fever: sudden onset, 4 days duration (range 38-40 C)',
        '- Severe myalgia and arthralgia: lower limbs most affected [WARNING SIGN]',
        '- Intense retro-orbital pain: worsens on eye movement',
        '- Maculopapular rash: trunk and arms, appeared Day 4',
        '- Gum bleeding: mild, on brushing only [HAEMORRHAGIC WARNING SIGN]',
        '- Persistent vomiting x3 in last 24 hours [WARNING SIGN — may indicate plasma leak]',
        '- Severe lethargy: unable to perform daily activities',
        '- Diffuse mild abdominal discomfort',
        '- Reduced urine output since yesterday [WARNING SIGN]',
    ],
    exam=[
        '- General: Flushed, febrile, fatigued; alert and oriented x3',
        '- Skin: Maculopapular non-blanching rash over trunk; petechiae bilateral forearms',
        '- Tourniquet test: POSITIVE (>20 petechiae in 1 sq inch) [Dengue Warning Sign]',
        '- Eyes: Conjunctival injection; retro-orbital tenderness on palpation',
        '- Abdomen: Hepatomegaly (liver palpable 1.5cm BCM); no ascites by clinical exam',
        '- Lymph nodes: Mild anterior cervical and inguinal lymphadenopathy',
        '- CVS: Regular rate; relative bradycardia for fever level; no murmurs',
        '- Respiratory: Clear bilaterally; no pleural rub',
    ],
    labs=[
        '- WBC: 2,800/uL [LEUCOPENIA — Normal 4,000-11,000]',
        '- Platelets: 68,000/uL [THROMBOCYTOPENIA — monitor every 4 hours]',
        '- Haematocrit: 49% [Rising from baseline ~43% — HAEMOCONCENTRATION]',
        '- Dengue NS1 Antigen: POSITIVE',
        '- Dengue IgM: Positive  |  Dengue IgG: Negative (primary infection)',
        '- Dengue PCR: Sent — pending',
        '- ALT (SGPT): 98 U/L [Mild elevation — hepatitis]',
        '- AST (SGOT): 112 U/L [Mild elevation]',
        '- Serum Albumin: 3.2 g/dL [Mildly low — monitor for plasma leakage]',
        '- Urine: Mild proteinuria; no haematuria',
        '- Ultrasound Abdomen: Trace pericolic free fluid; hepatomegaly; no significant ascites',
    ],
    impression=(
        'Dengue Fever Day 4: NS1 antigen positive, primary dengue infection. '
        'Grade II Dengue Haemorrhagic Fever — multiple warning signs present: '
        'gum bleeding, thrombocytopenia trending down (68K), haemoconcentration, '
        'persistent vomiting, and trace free abdominal fluid on ultrasound. '
        'High risk of progression to Dengue Shock Syndrome within next 24-48 hours. '
        'Hospitalisation strongly recommended for close fluid and platelet monitoring.'
    ),
    plan=[
        '1. ADMIT TO WARD: strict fluid balance monitoring; IV access established',
        '2. Oral/IV hydration: target urine output 0.5-1 mL/kg/hour',
        '3. Paracetamol for fever/pain ONLY — AVOID aspirin, ibuprofen, NSAIDs (bleeding risk)',
        '4. Platelet count every 4 hours; haematocrit every 6 hours',
        '5. IV Normal Saline 0.9% if oral intake inadequate or haematocrit rises >20%',
        '6. Platelet transfusion threshold: platelets <10,000/uL or active significant bleeding',
        '7. Alert criteria: active bleeding, BP drop, cold extremities, severe abdominal pain',
        '8. Bed rest; mosquito net in ward to prevent intra-hospital spread',
        '9. Dietary: soft diet, adequate fluids (ORS); monitor weight daily for fluid shift',
        '10. Discharge criteria: platelets rising above 50,000, afebrile >24h, clinically stable',
    ],
    risk_label='MODERATE RISK — HOSPITALISATION RECOMMENDED — 4-HOURLY MONITORING',
    risk_color=ORG,
)

print('\nAll 3 PDF reports generated successfully.')
print('Files saved to: d:\\astrava\\samples\\')
