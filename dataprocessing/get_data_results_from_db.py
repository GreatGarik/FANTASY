import asyncio
from database.database import get_grandprix_results, get_actual_gp_async, select_all_teams_engines, get_duel_pair

POINTS_RACE = {1: 25, 2: 22, 3: 20, 4: 18, 5: 17, 6: 16, 7: 15, 8: 14, 9: 13, 10: 12, 11: 10, 12: 9, 13: 8, 14: 7,
               15: 6, 16: 5, 17: 4, 18: 3, 19: 2, 20: 1, 21: 0, 22: 0}
POINTS_RACE_TE = {1: 8, 2: 5, 3: 3, 4: 2, 5: 1}

POINTS_SPRINT = {1: 15, 2: 12, 3: 10, 4: 8, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
POINTS_SPRINT_TE = {1: 6, 2: 4, 3: 2, 4: 1}

POINTS_QUALI = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
POINTS_QUALI_TE = {1: 5, 2: 3, 3: 1}

async def get_res_gp():
    results_f1 = await get_grandprix_results(await get_actual_gp_async())
    teams_engines_dict = await select_all_teams_engines()
    results_gp = {}
    results_gp_drivers_by_stage = {} # Очки по частям, гонки, спринт, квалификация, лучший круг
    results_gp_duels = {}

    for key, value in teams_engines_dict.items():
        #results_gp.setdefault(key, 0)
        results_gp_drivers_by_stage.setdefault(key, {'sprint': 0, 'quali': 0, 'race': 0, 'bestlap': 0})
        results_gp_drivers_by_stage.setdefault('team_' + value[0], {'sprint': 0, 'quali': 0, 'race': 0, 'bestlap': 0})
        results_gp_drivers_by_stage.setdefault('engine_' + value[1], {'sprint': 0, 'quali': 0, 'race': 0, 'bestlap': 0})


    if results_f1['race_result']:
        for num, line in enumerate(results_f1['race_result'].split('\n'), 1):
            if not line.startswith('gap') and not line.startswith('laps') and not line.startswith('bestlap') and not line.startswith('DNF'):
                results_gp.setdefault(line.strip(), POINTS_RACE[num])
                results_gp_drivers_by_stage[line.strip()]['race'] += POINTS_RACE.get(num, 0) # по частям
                team, engine = teams_engines_dict.get(line.strip())
                results_gp['team_' + team] = results_gp.get('team_' + team, 0) + POINTS_RACE_TE.get(num, 0)
                results_gp_drivers_by_stage['team_' + team]['race'] += POINTS_RACE_TE.get(num, 0)  # по частям
                results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + POINTS_RACE_TE.get(num, 0)
                results_gp_drivers_by_stage['engine_' + engine]['race'] += POINTS_RACE_TE.get(num, 0)  # по частям
            elif line.startswith('bestlap'):
                results_gp[line.split(':')[-1].strip()] = results_gp.get(line.split(':')[-1].strip(), 0) + 3
                results_gp_drivers_by_stage[line.split(':')[-1].strip()]['bestlap'] = 3  # по частям
                team, engine = teams_engines_dict.get(line.split(':')[-1].strip())
                results_gp['team_' + team] = results_gp.get('team_' + team, 0) + 2
                results_gp_drivers_by_stage['team_' + team]['bestlap'] = 2  # по частям
                results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + 1
                results_gp_drivers_by_stage['engine_' + engine]['bestlap'] = 1  # по частям
            elif not line.startswith('DNF'):
                key, value = line.strip().split(':')
                results_gp.setdefault(key, int(value))

            # порядок для дуэлей
            if not line.startswith('gap') and not line.startswith('laps') and not line.startswith('bestlap'):
                if not line.startswith('DNF'):
                    results_gp_duels.setdefault(line.strip(), num)
                else:
                    results_gp_duels[line.split(':')[-1].strip()] = num


    if results_f1['quali_result']:
        for num, line in enumerate(results_f1['quali_result'].split('\n'), 1):
            results_gp[line.strip()] = results_gp.get(line.strip(), 0) + POINTS_QUALI.get(num, 0)
            results_gp_drivers_by_stage[line.strip()]['quali'] += POINTS_QUALI.get(num, 0)  # по частям
            team, engine = teams_engines_dict.get(line.strip())
            results_gp['team_' + team] = results_gp.get('team_' + team, 0) + POINTS_QUALI_TE.get(num, 0)
            results_gp_drivers_by_stage['team_' + team]['quali'] += POINTS_QUALI_TE.get(num, 0)  # по частям
            results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + POINTS_QUALI_TE.get(num, 0)
            results_gp_drivers_by_stage['engine_' + engine]['quali'] += POINTS_QUALI_TE.get(num, 0)  # по частям

    if results_f1['sprint_result']:
        for num, line in enumerate(results_f1['sprint_result'].split('\n'), 1):
            results_gp[line.strip()] = results_gp.get(line.strip(), 0) + POINTS_SPRINT.get(num, 0)
            results_gp_drivers_by_stage[line.strip()]['sprint'] += POINTS_SPRINT.get(num, 0)  # по частям
            team, engine = teams_engines_dict.get(line.strip())
            results_gp['team_' + team] = results_gp.get('team_' + team, 0) + POINTS_SPRINT_TE.get(num, 0)
            results_gp_drivers_by_stage['team_' + team]['sprint'] += POINTS_SPRINT_TE.get(num, 0)  # по частям
            results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + POINTS_SPRINT_TE.get(num, 0)
            results_gp_drivers_by_stage['engine_' + engine]['sprint'] += POINTS_SPRINT_TE.get(num, 0)  # по частям

    #print(results_gp_drivers_by_stage)

    # создаем очки дуэлянтам
    winners_duels= {}
    duelists = await get_duel_pair(gp_value=await get_actual_gp_async())
    for item in duelists:
        if results_gp_duels.get(item[0], 0) < results_gp_duels.get(item[1], 0):
            winners_duels[item[0]] = 3
            winners_duels[item[1]] = 0
        else:
            winners_duels[item[1]] = 3
            winners_duels[item[0]] = 0

    return results_gp, results_gp_drivers_by_stage, winners_duels

if __name__ == '__main__':
    print(asyncio.run(get_res_gp()))
