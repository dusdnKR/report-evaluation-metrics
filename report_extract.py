import pandas as pd
import re

def extractFindingsImpression(report):
    findingsMatch = re.search(r'FINDINGS:(.*?)(?:IMPRESSION:|$)', report, re.DOTALL)
    impressionMatch = re.search(r'IMPRESSION:(.*)(?:Note:|$)', report, re.DOTALL)
    
    findings = findingsMatch.group(1).strip() if findingsMatch else ""
    impression = impressionMatch.group(1).strip() if impressionMatch else ""

    findings = findings.replace('\n', ' ')
    impression = impression.replace('\n', ' ')

    findings = findings.replace(' ___', '')
    impression = impression.replace(' ___', '')

    findings = re.sub(r'\s+', ' ', findings)
    impression = re.sub(r'\s+', ' ', impression)

    findings = "FINDINGS: " + findings
    impression = "IMPRESSION: " + impression
    
    return findings, impression


filePath = "Z:/Medical_Report_Generation/0805_chexfusion_report/mimic_gt_report.csv"

df = pd.read_csv(filePath)
df[['Findings', 'Impression']] = df['report'].apply(lambda x: pd.Series(extractFindingsImpression(x)))

outputFilePath = "Z:/Medical_Report_Generation/0805_chexfusion_report/mimic_gt_report_processed.csv"
df.to_csv(outputFilePath, index=False)