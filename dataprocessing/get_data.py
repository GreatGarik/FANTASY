from database.database import select_team_engine


def get_res_gp():
    results_gp = {}

    POINTS_RACE = {1: 25, 2: 22, 3: 20, 4: 18, 5: 17, 6: 16, 7: 15, 8: 14, 9: 13, 10: 12, 11: 10, 12: 9, 13: 8, 14: 7,
                   15: 6, 16: 5, 17: 4, 18: 3, 19: 2, 20: 1}
    POINTS_RACE_TE = {1: 8, 2: 5, 3: 3, 4: 2, 5: 1}

    POINTS_SPRINT = {1: 15, 2: 12, 3: 10, 4: 8, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
    POINTS_SPRINT_TE = {1: 6, 2: 4, 3: 2, 4: 1}

    POINTS_QUALI = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
    POINTS_QUALI_TE = {1: 5, 2: 3, 3: 1}
    with open('race.txt', encoding='UTF-8') as file:
        for num, line in enumerate(file.readlines(), 1):
            if not line.startswith('gap') and not line.startswith('laps') and not line.startswith('bestlap'):
                results_gp.setdefault(line.strip(), POINTS_RACE[num])
                team, engine = select_team_engine(line.strip())
                results_gp['team_' + team] = results_gp.get('team_' + team, 0) + POINTS_RACE_TE.get(num, 0)
                results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + POINTS_RACE_TE.get(num, 0)
            elif line.startswith('bestlap'):
                results_gp[line.split(':')[-1].strip()] = results_gp.get(line.split(':')[-1].strip(), 0) + 3
                team, engine = select_team_engine(line.split(':')[-1].strip())
                results_gp['team_' + team] = results_gp.get('team_' + team, 0) + 2
                results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + 1
            else:
                key, value = line.strip().split()
                results_gp.setdefault(key, int(value))
    with open('sprint.txt', encoding='UTF-8') as file:
        for num, line in enumerate(file.readlines(), 1):
            results_gp[line.strip()] = results_gp.get(line.strip(), 0) + POINTS_SPRINT.get(num, 0)
            team, engine = select_team_engine(line.strip())
            results_gp['team_' + team] = results_gp.get('team_' + team, 0) + POINTS_SPRINT_TE.get(num, 0)
            results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + POINTS_SPRINT_TE.get(num, 0)

    with open('quali.txt', encoding='UTF-8') as file:
        for num, line in enumerate(file.readlines(), 1):
            results_gp[line.strip()] = results_gp.get(line.strip(), 0) + POINTS_QUALI.get(num, 0)
            team, engine = select_team_engine(line.strip())
            results_gp['team_' + team] = results_gp.get('team_' + team, 0) + POINTS_QUALI_TE.get(num, 0)
            results_gp['engine_' + engine] = results_gp.get('engine_' + engine, 0) + POINTS_QUALI_TE.get(num, 0)
    return results_gp

if __name__ == '__main__':
    print(get_res_gp())
