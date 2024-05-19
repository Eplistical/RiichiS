RANK_TEXT_MAP: dict[int, str] = {
    1: "一",
    2: "二",
    3: "三",
    4: "四",
}

def resolve_ranks(pts: list[int]) -> list[int]:
    """
    resolves player rank for a list of points, 
    and returns a list of ranks that are associated with input
    """
    pt_rank_map=dict()
    rank=1
    for pt in sorted(pts, reverse=True):
        if pt not in pt_rank_map:
            pt_rank_map[pt]=rank
        rank=rank+1
    return[pt_rank_map[pt] for pt in pts]

def get_adjusted_uma(ranks: list[int], uma: list[int]) -> list[int]:
    """Computes adjusted uma based on ranks

    When ranks are [1,2,3,4], no adjustment is applied.
    When some players have the same rank, (e.g. 1,1,3,4), these players split the uma.
    """
    sorted_ranks = sorted(ranks)
    adjusted_uma = []
    cur_rank = None
    i = 0
    j = 0
    while i < 4:
        j = i
        sum_uma = 0
        while j < 4 and sorted_ranks[j] == sorted_ranks[i]:
            sum_uma += uma[j]
            j += 1
        rst_uma = sum_uma / (j-i)
        adjusted_uma += [rst_uma] * (j-i)
        i = j
    return adjusted_uma 