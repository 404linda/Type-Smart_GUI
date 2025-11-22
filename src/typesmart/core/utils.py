def normalize(s):
    return " ".join(s.strip().split())

def progress_bar(current, total, width=20):
    if total <= 0:
        total = 1
    filled = int((current / total) * width)
    filled = max(0, min(width, filled))
    return "[" + "#" * filled + "-" * (width - filled) + "]"

def update_heatmap(key, correct, progress):
    hm = progress.setdefault("heatmap", {})
    if key not in hm:
        hm[key] = {"correct": 0, "wrong": 0}
    if correct:
        hm[key]["correct"] += 1
    else:
        hm[key]["wrong"] += 1
