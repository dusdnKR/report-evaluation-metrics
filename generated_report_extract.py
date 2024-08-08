import pandas as pd
import re

def extractFindingsImpression(report):
    if report.startswith("FINDINGS:"):
        findingsMatch = re.search(r'FINDINGS:(.*?)(?:IMPRESSION:|$)', report, re.DOTALL)
        impressionMatch = re.search(r'IMPRESSION:(.*?)(?:Note:|$)', report, re.DOTALL)
    elif report.startswith("IMPRESSION:"):
        impressionMatch = re.search(r'IMPRESSION:(.*?)(?:FINDINGS:|$)', report, re.DOTALL)
        findingsMatch = re.search(r'FINDINGS:(.*?)(?:Note:|$)', report, re.DOTALL)
    else:
        findingsMatch = re.search(r'FINDINGS:(.*?)(?:IMPRESSION:|$)', report, re.DOTALL)
        impressionMatch = re.search(r'IMPRESSION:(.*?)(?:Note:|$)', report, re.DOTALL)
    
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

def getNewFile(is_rag, is_gradcam, is_predict):
    fileName = f"rag_{is_rag}_gradcam_{is_gradcam}_predict_{is_predict}_remove_nan_cols_stage_2.csv"
    filePath = f"Z:/Medical_Report_Generation/0805_chexfusion_report/{fileName}"

    df = pd.read_csv(filePath)
    df[['Findings', 'Impression']] = df['Final Report'].apply(lambda x: pd.Series(extractFindingsImpression(x)))

    outputFilePath = f"Z:/Medical_Report_Generation/0805_chexfusion_report/{fileName[:-4]}_processed.csv"
    df.to_csv(outputFilePath, index=False)

getNewFile(False, True, True)
getNewFile(False, True, False)
getNewFile(False, False, True)
getNewFile(False, False, False)