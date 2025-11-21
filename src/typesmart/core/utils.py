def normalize(s): return ' '.join(s.strip().split())

def progress_bar(current,total,width=20): filled=int((current/total)*width); return '['+'#'*filled+'-'*(width-filled)+']'

def update_heatmap(key,correct,progress): hm=progress['heatmap']; hm.setdefault(key,{'correct':0,'wrong':0}); hm[key]['correct' if correct else 'wrong']+=1
