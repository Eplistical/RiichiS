import argparse 
from db_interface import DbInterface
from game_stats import GameStats
from game_stats import PlayerStats
from stats import get_aggregated_player_stats
from stats import generate_leader_board_excel
from pprint import pprint


def parse_player_stats(arg):
  vals = arg.split(',')
  if len(vals) == 5:
    # player,pt,riichi,agari,deal_in
    return PlayerStats(
      player_name=vals[0],
      points=int(vals[1]),
      riichi=int(vals[2]),
      agari=int(vals[3]),
      deal_in=int(vals[4])
    )
  else:
    print(f"invalid args for player stats: {vals}")

def parse_args():
  parser = argparse.ArgumentParser(
                      prog='RiichiStats',
                      description='Perform CURD operates on the riichi-stats database.')
  parser.add_argument('-m', '--mode', required=True, choices=['add_player', 'list_players', 'record_game', 'list_games', 'get_stats', 'init_db'])
  parser.add_argument('-p', '--player', type=str)
  parser.add_argument('-d', '--date', type=int)
  parser.add_argument('-s', '--start_date', type=int, default=0)
  parser.add_argument('-e', '--end_date', type=int, default=99999999)
  parser.add_argument('--east', type=parse_player_stats)
  parser.add_argument('--south', type=parse_player_stats)
  parser.add_argument('--west', type=parse_player_stats)
  parser.add_argument('--north', type=parse_player_stats)
  return parser.parse_args()

def print_game(game: GameStats):
  print(f'game_id = {game.game_id}, date = {game.date}')
  print(f'[東]{game.east_player_stats.player_name:>10}{game.east_player_stats.points:>7} 立{game.east_player_stats.riichi:<2}和{game.east_player_stats.agari:<2}铳{game.east_player_stats.deal_in:<2}')
  print(f'[南]{game.south_player_stats.player_name:>10}{game.south_player_stats.points:>7} 立{game.south_player_stats.riichi:<2}和{game.south_player_stats.agari:<2}铳{game.south_player_stats.deal_in:<2}')
  print(f'[西]{game.west_player_stats.player_name:>10}{game.west_player_stats.points:>7} 立{game.west_player_stats.riichi:<2}和{game.west_player_stats.agari:<2}铳{game.west_player_stats.deal_in:<2}')
  print(f'[北]{game.north_player_stats.player_name:>10}{game.north_player_stats.points:>7} 立{game.north_player_stats.riichi:<2}和{game.north_player_stats.agari:<2}铳{game.north_player_stats.deal_in:<2}')

def run_add_player(args):
  if not args.player:
    print(f'invalid player name {args.player}.')
  else:
    db = DbInterface()
    if db.player_exists(args.player):
      print(f'player {args.player} already exists.')
    else:
      db.add_player(args.player)
      print(f'player {args.player} added.')

def run_list_players(args):
  db = DbInterface()
  players = db.list_players()
  print(f"Players count: {len(players)}")
  for player in players:
    print(player)

def validate_player_stats(db: DbInterface, stats: PlayerStats):
  if not stats.player_name or not db.player_exists(stats.player_name):
    print(f'Player {stats.player_name} is not registered.')
    return False
  if stats.points is None:
    print(f'Invalid points {stats.points}.')
  return True

def run_record_game(args):
  db = DbInterface()
  if not args.east or not validate_player_stats(db, args.east):
    print(f'East player {args.east} invalid.')
    return
  if not args.south or not validate_player_stats(db, args.south):
    print(f'South player {args.south} invalid.')
    return
  if not args.west or not validate_player_stats(db, args.west):
    print(f'West player {args.west} invalid.')
    return
  if not args.north or not validate_player_stats(db, args.north):
    print(f'North player {args.north} invalid.')
    return
  if args.date is None:
    print(f'date {args.date} invalid.')
    return
  game = GameStats(game_id=None, date=args.date, 
                   east_player_stats=args.east,
                   south_player_stats=args.south,
                   west_player_stats=args.west,
                   north_player_stats=args.north)
  db.record_game(game)
  print('Game Recorded:')
  print_game(game)

def run_list_games(args):
  db = DbInterface()
  games = db.list_games(args.start_date, args.end_date)
  print(f"Listing games between {args.start_date} and {args.end_date}")
  print(f"Games count: {len(games)}")
  for game in games:
    print_game(game)
    print('-' * 32)

def run_get_stats(args):
  print(f"Generate stats between {args.start_date} and {args.end_date}")
  db = DbInterface()
  aggregated_stats = get_aggregated_player_stats(db, args.start_date, args.end_date)
  excel_file="leaderboard.xlsx"
  generate_leader_board_excel(aggregated_stats, outfile_name=excel_file)
  print(f"Exported to excel {excel_file}")

def run_init_db(args):
  db = DbInterface()
  db.init_db()

def run(args):
  if args.mode == 'add_player':
    run_add_player(args)
  elif args.mode == 'list_players':
    run_list_players(args)
  elif args.mode == 'record_game':
    run_record_game(args)
  elif args.mode == 'list_games':
    run_list_games(args)
  elif args.mode == 'get_stats':
    run_get_stats(args)
  elif args.mode == 'init_db':
    run_init_db(args)
  else:
    raise ValueError(f'Invalid mode {args.mode}')
    
if __name__ == '__main__':
  try:
    args = parse_args()
    run(args)
  except Exception as e:
    print(f"error occurred: {e}")