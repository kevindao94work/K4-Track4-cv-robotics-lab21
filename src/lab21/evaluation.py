import configparser,csv,json,shutil
from pathlib import Path
import numpy as np
import trackeval
from .mot_writer import validate_rows

def evaluate(gt_source,prediction,out,sequence='video_1',length=None):
    gt_source=Path(gt_source);prediction=Path(prediction);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    gt=np.loadtxt(gt_source,delimiter=',',ndmin=2);pred=validate_rows(np.loadtxt(prediction,delimiter=',',ndmin=2))
    if gt.shape[1]!=9 or not np.isfinite(gt).all():raise ValueError('Expected original 9-column MOT17 GT')
    if length is None:raise ValueError('Sequence length must come from trusted metadata')
    if gt[:,0].min()!=1 or gt[:,0].max()!=length or pred[:,0].max()>length:raise ValueError('GT/prediction alignment mismatch')
    gtd=out/'gt'/sequence/'gt';gtd.mkdir(parents=True,exist_ok=True);shutil.copy2(gt_source,gtd/'gt.txt')
    td=out/'trackers'/'selected'/'data';td.mkdir(parents=True,exist_ok=True);shutil.copy2(prediction,td/f'{sequence}.txt')
    cfg={'GT_FOLDER':str((out/'gt').resolve()),'TRACKERS_FOLDER':str((out/'trackers').resolve()),'BENCHMARK':'MOT17','SPLIT_TO_EVAL':'train','SKIP_SPLIT_FOL':True,'SEQ_INFO':{sequence:length},'TRACKERS_TO_EVAL':['selected'],'CLASSES_TO_EVAL':['pedestrian'],'DO_PREPROC':True,'PRINT_CONFIG':False}
    dataset=trackeval.datasets.MotChallenge2DBox(cfg)
    evaluator=trackeval.Evaluator({'PRINT_CONFIG':False,'USE_PARALLEL':False,'PRINT_RESULTS':False,'OUTPUT_SUMMARY':True,'OUTPUT_DETAILED':True,'PLOT_CURVES':False})
    results,messages=evaluator.evaluate([dataset],[trackeval.metrics.HOTA(),trackeval.metrics.CLEAR(),trackeval.metrics.Identity()])
    if messages[dataset.get_name()]['selected']!='Success':raise RuntimeError(messages)
    scores=results[dataset.get_name()]['selected'][sequence]['pedestrian']
    metrics={'HOTA':float(np.mean(scores['HOTA']['HOTA'])*100),'DetA':float(np.mean(scores['HOTA']['DetA'])*100),'AssA':float(np.mean(scores['HOTA']['AssA'])*100),'MOTA':float(scores['CLEAR']['MOTA']*100),'IDF1':float(scores['Identity']['IDF1']*100),'IDSW':int(scores['CLEAR']['IDSW']),'FP':int(scores['CLEAR']['CLR_FP']),'FN':int(scores['CLEAR']['CLR_FN'])}
    return metrics
