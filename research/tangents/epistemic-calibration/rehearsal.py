"""T002: exact, entirely fictional two-signal Bayesian decision rehearsal.

No listener trials, acoustics, model fitting, or observational evidence.
"""
import argparse
import json
from itertools import product


def validate(p, hit, false, miss_cost, false_action_cost, check_hit, check_false, check_cost, delay_cost):
    for name, val in [('prevalence', p), ('hit', hit), ('false_alarm', false), ('check_hit', check_hit), ('check_false', check_false)]:
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not 0 <= val <= 1:
            raise ValueError(f'{name} must be a probability in [0,1]')
    for name, val in [('miss_cost', miss_cost), ('false_action_cost', false_action_cost), ('check_cost', check_cost), ('delay_cost', delay_cost)]:
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not 0 <= val < float('inf'):
            raise ValueError(f'{name} must be finite and nonnegative')
    if miss_cost + false_action_cost == 0:
        raise ValueError('at least one consequence cost must be positive')


def minimum_loss(hazard_mass, safe_mass, miss_cost, false_action_cost):
    """Choose act or ignore from unnormalised joint probability masses."""
    acting = safe_mass * false_action_cost
    ignoring = hazard_mass * miss_cost
    return (acting, 'act') if acting < ignoring else (ignoring, 'ignore')


def evaluate(prevalence, hit, false_alarm, miss_cost, false_action_cost,
             check_hit=.95, check_false=.05, check_cost=.05, delay_cost=0):
    validate(prevalence, hit, false_alarm, miss_cost, false_action_cost,
             check_hit, check_false, check_cost, delay_cost)
    # Each observation has joint masses (hazard, safe). Positive and negative alerts.
    obs = {
        'alert': (prevalence * hit, (1-prevalence) * false_alarm),
        'silence': (prevalence * (1-hit), (1-prevalence) * (1-false_alarm)),
    }
    forced = compliant = optimal = selective = 0.0
    confusion = {name: {'TP': 0., 'FP': 0., 'FN': 0., 'TN': 0.}
                 for name in ('alarm_compliance', 'bayes', 'forced_verify', 'selective_verify')}
    check_count = {'forced_verify': 0., 'selective_verify': 0.}
    outcomes = {}
    for label, (hazard, safe) in obs.items():
        minimum, action = minimum_loss(hazard, safe, miss_cost, false_action_cost)
        check_positive = minimum_loss(hazard*check_hit, safe*check_false,
                                      miss_cost, false_action_cost)[0]
        check_negative = minimum_loss(hazard*(1-check_hit), safe*(1-check_false),
                                      miss_cost, false_action_cost)[0]
        verified = (check_positive + check_negative +
                    (hazard+safe)*check_cost + hazard*delay_cost)
        # Joint (not conditional) confusion masses. These are mathematical expectations,
        # NOT observed responses or a population confusion matrix.
        pos_act = minimum_loss(hazard*check_hit, safe*check_false,
                               miss_cost, false_action_cost)[1] == 'act'
        neg_act = minimum_loss(hazard*(1-check_hit), safe*(1-check_false),
                               miss_cost, false_action_cost)[1] == 'act'
        checked_h = check_hit*pos_act + (1-check_hit)*neg_act
        checked_s = check_false*pos_act + (1-check_false)*neg_act
        immediate = float(action == 'act')
        compliance = float(label == 'alert')
        policies = {'alarm_compliance': (compliance, compliance),
                    'bayes': (immediate, immediate),
                    'forced_verify': (checked_h, checked_s),
                    'selective_verify': (checked_h, checked_s) if verified < minimum
                                        else (immediate, immediate)}
        for policy, (act_h, act_s) in policies.items():
            confusion[policy]['TP'] += hazard * act_h
            confusion[policy]['FN'] += hazard * (1-act_h)
            confusion[policy]['FP'] += safe * act_s
            confusion[policy]['TN'] += safe * (1-act_s)
        check_count['forced_verify'] += hazard+safe
        check_count['selective_verify'] += (hazard+safe) if verified < minimum else 0
        optimal += minimum
        forced += verified
        selective += min(minimum, verified)
        compliant += safe * false_action_cost if label == 'alert' else hazard * miss_cost
        mass = hazard + safe
        outcomes[label] = {
            'observation_probability': round(mass, 9),
            'hazard_posterior': round(hazard/mass, 9) if mass else None,
            'bayes_action': action if mass else 'unobserved',
            'verify_if_beneficial': verified < minimum if mass else False,
        }
    ppv_mass = sum(obs['alert'])
    npv_mass = sum(obs['silence'])
    return {
        'synthetic': True,
        'prevalence': prevalence, 'hit': hit, 'false_alarm': false_alarm,
        'miss_cost': miss_cost, 'false_action_cost': false_action_cost,
        'check_hit': check_hit, 'check_false': check_false,
        'check_cost': check_cost, 'delay_cost': delay_cost,
        'alert_ppv': round(obs['alert'][0]/ppv_mass, 9) if ppv_mass else None,
        'silence_hazard_probability': round(obs['silence'][0]/npv_mass, 9) if npv_mass else None,
        'observations': outcomes,
        'expected_confusion_per_1000': {
            policy: {cell: round(value*1000, 6) for cell, value in cells.items()}
            for policy, cells in confusion.items()},
        'expected_checks_per_1000': {key: round(value*1000, 6)
                                     for key, value in check_count.items()},
        'expected_loss': {k: round(v, 9) for k, v in (
            ('alarm_compliance', compliant), ('bayes', optimal),
            ('forced_verify', forced), ('selective_verify', selective))},
    }


def sweep():
    # Grid is a prespecified sensitivity demonstration, not estimated population data.
    cases = []
    for p, hit, far, cost in product((.02, .2, .5), (.75, .95), (.05, .35), (1., 3.)):
        cases.append(evaluate(p, hit, far, miss_cost=5., false_action_cost=cost,
                              check_hit=.95, check_false=.05, check_cost=.1,
                              delay_cost=.25))
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='emit deterministic fictional grid')
    args = parser.parse_args()
    cases = sweep()
    if args.json:
        print(json.dumps({'schema':'mhac-t002-synthetic-v1', 'cases':cases}, sort_keys=True, indent=2, allow_nan=False))
    else:
        print(f'{len(cases)} synthetic cases; no measured human data')
        print('first case:', json.dumps(cases[0], sort_keys=True))


if __name__ == '__main__':
    main()
