difficulties = ['easy', 'medium', 'hard']

def get_best_scores():
    try:
        with open('../cache/scores', 'r', encoding='utf-8') as f:
            return eval(f.read())
    except FileNotFoundError:
        return None

def get_best_scores_for_difficulty(difficulty):
    scores = get_best_scores()
    if not scores:
        return 1
    else:
        return scores[difficulty]

def set_best_scores(wave, difficulty):
    scores = get_best_scores()
    updated = False

    if not scores:
        scores = {d: 0 for d in difficulties}

    if scores[difficulty] < wave:
        scores[difficulty] = wave
        updated = True

    with open('../cache/scores', 'w', encoding='utf-8') as f:
        f.write(str(scores))

    return updated
