from typing import Optional
from game_stats import PlayerStats
from game_stats import AggregatedPlayerStats
from util import resolve_ranks
from util import get_adjusted_uma
from db_interface import DbInterface
from pandas import DataFrame

def aggregate_player_stats(aggregated_stats: dict[str, PlayerStats], player_stats: PlayerStats, player_rank: int, start_date: int, end_date: int, uma: list[int]) -> None:
    """helper function that aggregates a player's stats from a single hand"""
    player_name = player_stats.player_name
    if player_name not in aggregated_stats:
        aggregated_stats[player_name] = AggregatedPlayerStats(
        player_name=player_name,
        start_date=start_date,
        end_date=end_date,
        games_count=0,
        place_count_map={ k: 0 for k in range(1,5) },
        top_k_count_map={ k: 0 for k in range(1,5) },
        rank_sum=0,
        max_points=None,
        points_sum=0,
        points_sum_with_uma=0,
        riichi_sum=0,
        agari_sum=0,
        deal_in_sum=0,
        )
    # game count
    aggregated_stats[player_name].games_count += 1
    # rank count
    aggregated_stats[player_name].place_count_map[player_rank] += 1
    # top k count
    for k in range(player_rank, 5):
        aggregated_stats[player_name].top_k_count_map[k] += 1
    # rank sum 
    aggregated_stats[player_name].rank_sum += player_rank
    # max pt
    if aggregated_stats[player_name].max_points is None or aggregated_stats[player_name].max_points < player_stats.points:
        aggregated_stats[player_name].max_points = player_stats.points
    # points sum
    aggregated_stats[player_name].points_sum += player_stats.points
    # points sum with (adjusted) uma
    aggregated_stats[player_name].points_sum_with_uma += player_stats.points + round(uma[player_rank-1] * 1000)
    # riichi sum
    if player_stats.riichi is not None:
        aggregated_stats[player_name].riichi_sum += player_stats.riichi
    # agari sum
    if player_stats.agari is not None:
        aggregated_stats[player_name].agari_sum += player_stats.agari
    # deal-in sum
    if player_stats.deal_in is not None:
        aggregated_stats[player_name].deal_in_sum += player_stats.deal_in

def get_aggregated_player_stats(db: DbInterface, start_date: int, end_date: int, player_name: Optional[str]=None, uma: list[int]=[45,5,-15,-35]) -> dict[str, AggregatedPlayerStats]:
    """get aggregated stats for all games between two given dates, and potentially for a given player"""
    aggregated_stats = dict()
    for game in db.list_games(start_date, end_date, player_name):
        ranks = resolve_ranks([
            game.east_player_stats.points,
            game.south_player_stats.points,
            game.west_player_stats.points,
            game.north_player_stats.points,
        ])
        adjusted_uma = get_adjusted_uma(ranks, uma)
        aggregate_player_stats(aggregated_stats, game.east_player_stats, ranks[0], start_date, end_date, adjusted_uma)
        aggregate_player_stats(aggregated_stats, game.south_player_stats, ranks[1], start_date, end_date, adjusted_uma)
        aggregate_player_stats(aggregated_stats, game.west_player_stats, ranks[2], start_date, end_date, adjusted_uma)
        aggregate_player_stats(aggregated_stats, game.north_player_stats, ranks[3], start_date, end_date, adjusted_uma)
    return aggregated_stats

def generate_leader_board_excel(aggregated_player_stats: dict[str, AggregatedPlayerStats], 
                                outfile_name: str='leaderboard.xlsx', sheet_name: str='leaderboard') -> None:
    """output an excel file for leader board"""
    ranked_players = sorted(aggregated_player_stats.values(), key=lambda x: x.points_sum_with_uma, reverse=True)
    df = DataFrame({
        "顺位": list(range(1, len(ranked_players) + 1)),
        "": [""] * len(ranked_players),
        "选手名": map(lambda p: p.player_name, ranked_players),
        "总积分": map(lambda p: f'{round(p.points_sum_with_uma / 1000, 1):.1f}', ranked_players),
        "素点": map(lambda p: f'{round(p.points_sum / 1000, 1):.1f}', ranked_players),
        "试合数": map(lambda p: p.games_count, ranked_players),
        "平着": map(lambda p: round(p.rank_sum / p.games_count, 2), ranked_players),
        "1着": map(lambda p: p.place_count_map[1], ranked_players),
        "2着": map(lambda p: p.place_count_map[2], ranked_players),
        "3着": map(lambda p: p.place_count_map[3], ranked_players),
        "4着": map(lambda p: p.place_count_map[4], ranked_players),
        "TOP率": map(lambda p: f'{round(p.top_k_count_map[1] / p.games_count * 100, 2)}%', ranked_players),
        "连对率": map(lambda p: f'{round(p.top_k_count_map[2] / p.games_count * 100, 2)}%', ranked_players),
        "四位回避": map(lambda p: f'{round(p.top_k_count_map[3] / p.games_count * 100, 2)}%', ranked_players),
        "最高得点": map(lambda p: p.max_points, ranked_players),
        "平均得点": map(lambda p: round(p.points_sum / p.games_count), ranked_players),
    })
    df.to_excel(outfile_name, sheet_name=sheet_name, index=False)
