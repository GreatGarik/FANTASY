from dataprocessing.get_data import get_res_gp
from database.database import get_predict, select_drivers, add_result, get_result, add_points


def calculation_drivers(gp):
    deltas = {0: 10, 1: 7, 2: 5, 3: 3, 4: 2, 5: 1}
    predicts_from_db = get_predict(gp)
    results_predict_gp = get_res_gp()

    names = [i.driver_name for i in select_drivers()]
    first_max = max([results_predict_gp[name] for name in names])
    names = [i.driver_name for i in select_drivers()[10:]]
    second_max = max([results_predict_gp[name] for name in names])
    names = [i.driver_name for i in select_drivers()[15:]]
    third_max = max([results_predict_gp[name] for name in names])

    for predict in predicts_from_db:
        counter_best = 0
        max_best = []
        max_not_best = []
        counter_lap_gap = 0
        if results_predict_gp.get(predict.first_driver) == first_max or results_predict_gp.get(
                predict.second_driver) == first_max:
            counter_best += 1
            max_best.append(first_max)

        if results_predict_gp.get(predict.first_driver) == first_max and results_predict_gp.get(
                predict.second_driver) == first_max:
            max_not_best.append(first_max)
        elif results_predict_gp.get(predict.first_driver) != first_max and results_predict_gp.get(
                predict.second_driver) != first_max:
            max_not_best.append(results_predict_gp.get(predict.first_driver))
            max_not_best.append(results_predict_gp.get(predict.second_driver))
        elif results_predict_gp.get(predict.first_driver) != first_max:
            max_not_best.append(results_predict_gp.get(predict.first_driver))
        else:
            max_not_best.append(results_predict_gp.get(predict.second_driver))

        if results_predict_gp.get(predict.third_driver) == second_max:
            counter_best += 1
            max_best.append(second_max)
        else:
            max_not_best.append(results_predict_gp.get(predict.third_driver))

        if results_predict_gp.get(predict.fourth_driver) == third_max:
            counter_best += 1
            max_best.append(third_max)
        else:
            max_not_best.append(results_predict_gp.get(predict.fourth_driver))

        if results_predict_gp['gap'] == predict.gap:
            counter_lap_gap += 1
        if results_predict_gp['laps'] == predict.lapped:
            counter_lap_gap += 1

        if len(max_best) < 3:
            max_best.extend([0] * (3 - len(max_best)))

        if len(max_not_best) < 4:
            max_not_best.extend([0] * (4 - len(max_not_best)))


        max1_best, max2_best, max3_best = sorted(max_best, reverse=True)
        max1_not_best, max2_not_best, max3_not_best, max4_not_best = sorted(max_not_best, reverse=True)

        delta_gap = abs(results_predict_gp['gap'] - predict.gap)
        delta_laps = abs(results_predict_gp['laps'] - predict.lapped)
        max_lap_gap = max(deltas.get(delta_gap, 0), deltas.get(delta_laps, 0))
        add_result(predict.user_id, results_predict_gp.get(predict.first_driver),
                   results_predict_gp.get(predict.second_driver),
                   results_predict_gp.get(predict.third_driver), results_predict_gp.get(predict.fourth_driver),
                   results_predict_gp.get('team_' + predict.driver_team),
                   results_predict_gp.get('engine_' + predict.driver_engine),
                   deltas.get(delta_gap, 0), deltas.get(delta_laps, 0), counter_best, max1_best, max2_best, max3_best,
                   max1_not_best, max2_not_best, max3_not_best, max4_not_best, counter_lap_gap, max_lap_gap,
                   predict.penalty, gp)


    data = get_result(gp)

    POINST_GP = {1: 100, 2: 92, 3: 86, 4: 80, 5: 75, 6: 70, 7: 66, 8: 62, 9: 58, 10: 55, 11: 52, 12: 49, 13: 46, 14: 44,
                 15: 42, 16: 40, 17: 38, 18: 36, 19: 34, 20: 32, 21: 30, 22: 29, 23: 28, 24: 27, 25: 26, 26: 25, 27: 24,
                 28: 23, 29: 22, 30: 21, 31: 20, 32: 19, 33: 18, 34: 17, 35: 16, 36: 15, 37: 14, 38: 13, 39: 12, 40: 11,
                 41: 10, 42: 9, 43: 8, 44: 7, 45: 6, 46: 5, 47: 4, 48: 3, 49: 2, 50: 1}

    for index, (user, result) in enumerate(data, 1):
        add_points(user.id, 2024, POINST_GP.get(index, 0), gp)