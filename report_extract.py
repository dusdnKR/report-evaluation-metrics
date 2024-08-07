import pandas as pd
import re

def extract_findings_impression(report):
    findings_match = re.search(r'FINDINGS:(.*?)(?:IMPRESSION:|$)', report, re.DOTALL)
    impression_match = re.search(r'IMPRESSION:(.*)', report, re.DOTALL)
    
    findings = findings_match.group(1).strip() if findings_match else ""
    impression = impression_match.group(1).strip() if impression_match else ""

    findings = findings.replace('\n', ' ')
    impression = impression.replace('\n', ' ')

    findings = findings.replace(' ___', '')
    impression = impression.replace(' ___', '')

    findings = re.sub(r'\s+', ' ', findings)
    impression = re.sub(r'\s+', ' ', impression)

    findings = "FINDINGS: " + findings
    impression = "IMPRESSION: " + impression
    
    return findings, impression


file_path = "Z:/Medical_Report_Generation/0805_chexfusion_report/mimic_gt_report.csv"

df = pd.read_csv(file_path)
df[['Findings', 'Impression']] = df['report'].apply(lambda x: pd.Series(extract_findings_impression(x)))

output_file_path = "Z:/Medical_Report_Generation/0805_chexfusion_report/mimic_gt_report_processed.csv"
df.to_csv(output_file_path, index=False)