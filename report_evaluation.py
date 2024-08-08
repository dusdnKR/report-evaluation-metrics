import pandas as pd
from tqdm import tqdm
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
# from cider.cider import Cider
from bert_score import BERTScorer
from transformers import logging
logging.set_verbosity_error()

def calcScores(dfPredicted, dfGroundTruth, compColName='report'):
    def calcBLEU(reference, prediction, smoothie):
        reference = [reference.split()]
        prediction = prediction.split()

        bleu1 = sentence_bleu(reference, prediction, weights=(1, 0, 0, 0), smoothing_function=smoothie)
        bleu2 = sentence_bleu(reference, prediction, weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)
        bleu3 = sentence_bleu(reference, prediction, weights=(0.33, 0.33, 0.33, 0), smoothing_function=smoothie)
        bleu4 = sentence_bleu(reference, prediction, smoothing_function=smoothie)  # Default weights for BLEU-4
        
        return (bleu1, bleu2, bleu3, bleu4)

    def calcROUGE(reference, prediction):
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge = scorer.score(reference, prediction)

        return rouge

    def calcBERT(reference, prediction, scorer):
        bertPrecision, bertRecall, bertF1 = scorer.score([prediction], [reference])
        bertPrecision, bertRecall, bertF1 = bertPrecision.item(), bertRecall.item(), bertF1.item() # Convert Datatype (tensor -> float)

        return (bertPrecision, bertRecall, bertF1)

    def calcCIDEr():
        # Gonna be edited..
        return 0
    
    study_id = []
    references = []
    predictions = []
    scoresBLEU = []
    scoresROUGE = []
    scoresBERT = []

    smoothie = SmoothingFunction().method1 # SmoothingFunction for BLEU Score
    scorer = BERTScorer(lang="en", rescale_with_baseline=False)  # BERTScorer for BERT Score
    for index, row in tqdm(dfPredicted.iterrows(), total=dfPredicted.shape[0]):
        if index in dfGroundTruth.index:
            reference = dfGroundTruth.loc[index, compColName]
            prediction = row[compColName]
            if reference != "" and prediction != "":
                study_id.append(index)
                references.append(reference)
                predictions.append(prediction)
                scoresBLEU.append(calcBLEU(reference, prediction, smoothie))
                scoresROUGE.append(calcROUGE(reference, prediction))
                scoresBERT.append(calcBERT(reference, prediction, scorer))
    
    dfResult = pd.DataFrame(study_id, columns=['study_id'])
    dfResult['reference'] = [reference for reference in references]
    dfResult['prediction'] = [prediction for prediction in predictions]

    # Add BLEU Score
    dfResult['BLEU-1'] = [score[0] for score in scoresBLEU]
    dfResult['BLEU-2'] = [score[1] for score in scoresBLEU]
    dfResult['BLEU-3'] = [score[2] for score in scoresBLEU]
    dfResult['BLEU-4'] = [score[3] for score in scoresBLEU]

    # Add ROUGE Score
    dfResult['ROUGE-1 F1'] = [score['rouge1'].fmeasure for score in scoresROUGE]
    dfResult['ROUGE-2 F1'] = [score['rouge2'].fmeasure for score in scoresROUGE]
    dfResult['ROUGE-L F1'] = [score['rougeL'].fmeasure for score in scoresROUGE]

    # Add BERT Score
    dfResult['BERT Precision'] = [score[0] for score in scoresBERT]
    dfResult['BERT Recall'] = [score[1] for score in scoresBERT]
    dfResult['BERT F1'] = [score[2] for score in scoresBERT]

    # Calculate Mean & Std
    scores = dfResult.columns[3:]
    means = dfResult[scores].mean()
    stds = dfResult[scores].std()
    dfResult.loc['mean'] = ['mean'] * 3 + list(means)
    dfResult.loc['std'] = ['std'] * 3 + list(stds)

    return dfResult


# is_rag, is_gradcam, is_predict = False, True, False
def Tempfunction0806(is_rag, is_gradcam, is_predict):
    rootPath = "Z:/Medical_Report_Generation/0805_chexfusion_report"
    # generatedReportName = f"rag_{is_rag}_gradcam_{is_gradcam}_predict_{is_predict}.csv"
    generatedReportName = f"rag_{is_rag}_gradcam_{is_gradcam}_predict_{is_predict}_remove_nan_cols_stage_2_processed.csv"
    generatedReportPath = f"{rootPath}/{generatedReportName}"

    # Read CSV Files
    print(f"Reading {generatedReportPath}...")
    reportGenerated = pd.read_csv(generatedReportPath, index_col='study_id').fillna("")
    reportGroundTruth = pd.read_csv(f"{rootPath}/mimic_gt_report_processed.csv", index_col='study_id').fillna("")

    # Add 'report' (= Findings + Impression) Col
    print("Adding a 'report' (= Findings + Impression) Column..")
    reportGenerated['report'] = reportGenerated['Findings'] + " " + reportGenerated['Impression']
    # reportGenerated['report'] = reportGenerated['Final Report']
    reportGroundTruth['report'] = reportGroundTruth['Findings'] + " " + reportGroundTruth['Impression']

    # Test Result
    compColNames = ['Findings', 'Impression', 'report']
    compColNames = ['report']
    for compColName in compColNames:
        print(f"Processing {compColName} Column...")
        results_df = calcScores(reportGenerated, reportGroundTruth, compColName)

        # Save the result
        print("Saving the result...")
        results_df.to_csv(f"{rootPath}/report_evaluation_metrics/{generatedReportName[:-4]}_{compColName.lower()}.csv", index=False)

Tempfunction0806(False, True, True)
Tempfunction0806(False, True, False)
# Tempfunction0806(False, False, True)
# Tempfunction0806(False, False, False)