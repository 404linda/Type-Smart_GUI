import json,os
PROGRESS_FILE=os.path.expanduser('~/.typing_progress_gui_v10.json')

def load_progress():
    if os.path.exists(PROGRESS_FILE): return json.load(open(PROGRESS_FILE))
    return {'theme':'neon','level':1,'current_set':0,'total_words':0,'total_errors':0,'total_time':0.0,'heatmap':{},'streak':0,'last_practice':'','custom_lessons':[]}

def save_progress(progress):
    tmp=PROGRESS_FILE+'.tmp'
    json.dump(progress,open(tmp,'w'))
    os.replace(tmp,PROGRESS_FILE)
