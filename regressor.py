import math

import pandas as pd
from matplotlib import pyplot as plt
import statsmodels.api as sm

ABILITIES = ['Sentinel', 'Raid', 'Overwhelm', 'Shielded', 'Ambush', 'Saboteur', 'Restore', 'Grit']

# need to rework abilities code

ASPECTS = ['Command',  'Aggression', 'Villainy',
           'Cunning', 'Vigilance']  # using Heroism as a holdout

base_features = ['adj_total_stats', 'arena', ]

sqrt_features = ['cost', 'sqrt_cost', 'arena']

sqr_features = ['cost', 'sqr_cost', 'arena']

simple_stat_features = ['power', 'hp', 'arena']

total_stat_features = ['total_power', 'total_hp', 'arena']

cost_features = ['cost']


def read_csv(path: str = 'data/card_data_sor_complete.csv') -> pd.DataFrame:
    """
    read a csv of SWU cards and turn them into pandas
    :param path: path to a csv of cards
    :return: a PD dataframe of the cards
    """
    raw_df = pd.read_csv(path)
    return raw_df


def get_units(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    parse out only units from the dataframe
    :param raw_df: a df of cards from SWUDB
    :return: a df of just units
    """
    unit_only_df = raw_df[raw_df['card type'] == "Unit"].copy()
    unit_only_df.reset_index(inplace=True, drop=True)
    unit_only_df.fillna(0,inplace=True)
    return unit_only_df


def make_ability_features(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a 1-hot column checking if an ability is in the text
    :param unit_df: a df of units
    :return: a df with an additional 1-hot column checking for a word
    """
    for ability in ABILITIES:
        output_col = pd.DataFrame()
        for col in ['keyword_1', 'keyword_2']:
            check_col = unit_df[col].str.match(ability)
            check_col.fillna(0, inplace=True)
            check_col = check_col.astype(int)
            value_col = unit_df[col].str.extract('(\d+)')
            value_col.fillna(1, inplace=True)
            value_col = value_col[0].astype(int)
            output_col[col] = check_col*value_col
        final_col = output_col.sum(axis=1)
        unit_df.loc[:, f"{ability}"] = final_col.copy()
    return unit_df


def make_unique(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make the uniqueness feature
    :param unit_df: a df of units
    :return: the same df with an additional uniqueness feature
    """

    uniqueness = unit_df['unique'].astype(int)
    unit_df.loc[:, 'uniqueness'] = uniqueness.copy()
    return unit_df


def make_sqrt_cost_feature(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a sqrt-cost feature
    :param unit_df: a df of units
    :return: a df with an additional sqrt_cost feature
    """
    sqrt_cost = unit_df['cost'].apply(math.sqrt)
    unit_df.loc[sqrt_cost.index, 'sqrt_cost'] = sqrt_cost.copy()
    return unit_df


def make_sqr_cost_feature(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a squared cost feature
    :param unit_df: a df of units
    :return: a df with an additional sqr_cost feature
    """
    sqr_cost = unit_df['cost']**2
    unit_df.loc[:, 'sqr_cost'] = sqr_cost.copy()
    return unit_df


def make_fit(x_cols: list, y_col: str, unit_df: pd.DataFrame, const: bool = True) -> (pd.DataFrame, sm.regression):
    """
    make a linear fit to some data
    :param x_cols: X columns to use
    :param y_col: value to fit to
    :param unit_df: df of Units
    :param const: include a constant?
    :return: the DF + a column of predicted values and the regression
    """
    X = unit_df[x_cols]
    y = unit_df[y_col]
    if const:
        X = sm.add_constant(X)
    results = sm.OLS(y, X).fit()
    print(results.summary())
    pred = results.predict(X)
    unit_df.loc[:, 'predictions'] = pred.copy()
    return unit_df, results


def make_aspect_features(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    makes a column of if a card has an aspect and how many times it appears
    :param unit_df: a df of units
    :return:
    """
    for aspect in ASPECTS:
        check_col = unit_df['aspects'].str.count(aspect)
        check_col = check_col.fillna(0)
        unit_df.loc[:, f"{aspect}"] = check_col.astype(int).copy()
    return unit_df


def make_total_stats(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    makes a column  for the total stat value of a unit
    :param unit_df: a df of units
    :return:
    """
    total_power = unit_df['power'] + unit_df['invisiblepower']
    total_hp = unit_df['hp'] + unit_df['invisiblehp']
    total_base = unit_df['power'] + unit_df['hp']
    combined_total = total_power + total_hp
    d = {'total_power': total_power, 'total_hp':total_hp,
                'total_base':total_base, 'combined_total':combined_total}
    for col in d:
        unit_df.loc[unit_df.index, col] = d[col].loc[:]
    return unit_df


def make_adj_total_stats(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    makes a column  for the total stat value of a unit
    :param unit_df: a df of units
    :return:
    """
    adj_col = unit_df['power']*2 + unit_df['hp']
    unit_df.loc[adj_col.index, 'adj_stats'] = adj_col.copy()
    adj_col = unit_df['total_power']*2 + unit_df['total_hp']
    unit_df.loc[adj_col.index, 'adj_total_stats'] = adj_col.copy()
    return unit_df


def count_aspects(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    Count the number of aspects for a unit
    :param unit_df: df of units
    :return: df of units with the n_aspects feature added
    """
    n_aspects = unit_df.aspects.str.count(',') + 1
    unit_df['n_aspects'] = n_aspects.fillna(0).astype(int)
    return unit_df


def make_plot(unit_df: pd.DataFrame, y_col: str, x_col: str) -> None:
    """
    make a plot of the results of a regression. Should probably be refactored to be more generic
    :param unit_df: df of units
    :param y_col: Y-variable
    :param x_col: X variable
    :return:
    """
    with plt.xkcd():
        plt.clf()
        plt.plot(unit_df[x_col], unit_df[y_col], color='r', marker='o',
                 linestyle='None', label=f'Observed {y_col}')
        plt.plot(unit_df[x_col], unit_df.predictions, color='b', marker='o',
                 linestyle='None', label=f'Predicted {y_col}')
        simple_line_y = []
        simple_line_x = []
        for i in range(1,11):
            simple_line_x.append(i)
            simple_line_y.append(.5 + 3*i)
        plt.plot(simple_line_x, simple_line_y, 'k-', label='Simple Linear Fit')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend()
        plt.show()


def calc_errors(unit_df: pd.DataFrame, y_col: str, asc=False) -> pd.DataFrame:
    unit_df.loc[unit_df.index, 'error'] = (unit_df[y_col] - unit_df['predictions']).copy()
    print(unit_df.sort_values('error', ascending=asc)[['name',  y_col, 'predictions', 'error']].head(5))

    unit_df.loc[:, 'percent_error'] = ((unit_df[y_col] - unit_df['predictions'])/unit_df[y_col]).copy()
    print(unit_df.sort_values('percent_error', ascending=asc)[['name', y_col, 'predictions', 'percent_error']].head(5))
    return unit_df


def make_qq(fit):
    with plt.xkcd():
        res = fit.resid  # residuals
        sm.qqplot(res)
        plt.show()
