import math

import pandas as pd
from matplotlib import pyplot as plt
import statsmodels.api as sm

ABILITIES = ['damage', 'sentinel', 'draw',
             'raid', ]  # 'grit', 'overwhelm','shielded', 'ambush', 'saboteur', 'restore'

ASPECTS = ['Command', 'Heroism', 'Aggression', 'Villainy',
           'Cunning', 'Vigilance']

base_features = ['adj_total_stats', 'arena', ]

sqrt_features = ['cost', 'sqrt_cost']

sqr_features = ['cost', 'sqr_cost']

stat_features = ['power', 'hp', 'arena']


def read_csv(path: str = 'data/cards_export_20230913.csv') -> pd.DataFrame:
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
    unit_only_df = raw_df[raw_df.case == "Unit"]
    unit_only_df.reset_index(inplace=True, drop=True)
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
            check_col = unit_df[col].str.contains(ability)
            check_col.fillna(0, inplace=True)
            check_col = check_col.astype(int)
            value_col = unit_df[col].str.extract('(\d+)')
            value_col.fillna(1, inplace=True)
            value_col = value_col[0].astype(int)
            output_col[col] = check_col*value_col
        final_col = output_col.sum(axis=1)
        unit_df[f"{ability}"] = final_col
    return unit_df


def make_sqrt_cost_feature(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a sqrt-cost feature
    :param unit_df: a df of units
    :return: a df with an additional sqrt_cost feature
    """
    sqrt_cost = unit_df['cost'].apply(math.sqrt)
    unit_df.loc[:, 'sqrt_cost'] = sqrt_cost
    return unit_df


def make_sqr_cost_feature(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a squared cost feature
    :param unit_df: a df of units
    :return: a df with an additional sqr_cost feature
    """
    sqr_cost = unit_df['cost']**2
    unit_df.loc[:, 'sqr_cost'] = sqr_cost
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
    unit_df['predictions'] = pred
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
        unit_df[f"{aspect}"] = check_col.astype(int)
    return unit_df


def make_total_stats(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    makes a column  for the total stat value of a unit
    :param unit_df: a df of units
    :return:
    """
    total_col = unit_df['power'] + unit_df['hp']
    unit_df['total_stats'] = total_col
    return unit_df


def make_adj_total_stats(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    makes a column  for the total stat value of a unit
    :param unit_df: a df of units
    :return:
    """
    adj_col = unit_df['power']*2 + unit_df['hp']
    unit_df.loc[:, 'adj_total_stats'] = adj_col
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
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend()
        plt.show()


def calc_errors(unit_df: pd.DataFrame, y_col: str, asc=False) -> pd.DataFrame:
    unit_df['error'] = unit_df[y_col] - unit_df['predictions']
    print(unit_df.sort_values('error', ascending=asc)[['name',  y_col, 'predictions', 'error']].head(5))

    unit_df['percent_error'] = (unit_df[y_col] - unit_df['predictions'])/unit_df[y_col]
    print(unit_df.sort_values('percent_error', ascending=asc)[['name', y_col, 'predictions', 'percent_error']].head(5))
    return unit_df


def make_qq(fit):
    with plt.xkcd():
        res = fit.resid  # residuals
        sm.qqplot(res)
        plt.show()


df = read_csv('data/card_export_20231209.csv')
unit_df = get_units(df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects]:
    unit_df = operation(unit_df)


# X_cols = base_features +keywords
# X_cols = base_features + ['n_aspects']
# X_cols = sqr_features
# X_cols = base_features

X_cols = sqr_features + ['arena']
unit_df, results = make_fit(x_cols=X_cols, y_col='adj_total_stats', unit_df=unit_df, const=True)
make_plot(unit_df, 'adj_total_stats', 'cost')
unit_df = calc_errors(unit_df, y_col='adj_total_stats', asc=False)
make_qq(results)

X_cols = stat_features
unit_df, results = make_fit(x_cols=X_cols, y_col='cost', unit_df=unit_df, const=False)
make_plot(unit_df, 'cost', 'adj_total_stats')
make_qq(results)
