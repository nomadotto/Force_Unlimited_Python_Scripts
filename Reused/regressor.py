import math

import pandas as pd
from matplotlib import pyplot as plt
import statsmodels.api as sm
import statsmodels.stats.weightstats as ws

pd.options.display.max_columns = None

ABILITIES = ['Sentinel', 'Raid', 'Overwhelm', 'Shielded', 'Ambush', 'Saboteur', 'Restore', 'Grit', 'Smuggle', 'Bounty',
             'Coordinate', 'Exploit', 'Piloting']

SOLID_ABILITIES = ['Bounty', 'Grit', 'Ambush', 'Shielded', 'Raid', 'Exploit', 'Sentinel']
# need to rework abilities code

SOLID_COST_ABILITIES = ['Sentinel', 'Raid', 'Shielded', 'Ambush', 'Restore', 'Grit', 'Bounty', 'Exploit', 'Makes_Droids',
                        'Makes_Clones', 'Ramps', 'Makes_X_Wings', 'Indirect', 'set_TWI', 'invisiblepower', 'invisiblehp']

ASPECTS = ['Command',  'Aggression', 'Villainy',
           'Cunning', 'Vigilance']  # using Heroism as a holdout

base_cost_features = ['cost', 'arena', ]

sqrt_features = ['cost', 'sqrt_cost', 'arena']

sqr_features = ['cost', 'sqr_cost', 'arena']

rarity_features = [f"rarity_{i}_dummy" for i in range(2,6)]

simple_stat_features = ['power', 'hp', 'arena']

total_stat_features = ['total_power', 'total_hp', 'arena']

invis_features = ['invisibledamage', 'invisibledraw']

cost_features = ['cost']

SETS = ['SHD', 'TWI', 'JTL']   # using SOR as baseline

POWER_ADJ = 6/5


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
    unit_only_df.fillna(0, inplace=True)
    return unit_only_df


def get_sets(cards_df: pd.DataFrame, sets: list) -> pd.DataFrame:
    """
    Pull out one or more sets worth of cards
    :param cards_df: a df of cards
    :param sets: the sets to grab
    :return: a df of cards from the sets indicated
    """
    sets_df = cards_df.loc[cards_df.loc[:, 'set'].isin(sets)].copy()
    sets_df.reset_index(inplace=True, drop=True)
    return sets_df


def make_set_features(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a feature for set the card came from
    :param unit_df: a df of units
    :return: df with a set feature as a one-hot
    """
    for set in SETS:
        unit_df.loc[:, f'set_{set}'] = (unit_df.loc[:, 'set'] == set).astype(int)
    return unit_df


def make_rarity_feature(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    make a feature to account for card rarity
    :param unit_df: a df of units
    :return: df with one-hot rarity features
    """
    dummies = pd.get_dummies(unit_df['rarity'],drop_first=True)
    for col in dummies.columns:
        unit_df[f"rarity_{col}_dummy"] = dummies[col].astype(int)
    return unit_df


def make_hacky_smuggle_bounty(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    do a hacky version of smuggle bounty until the data has been cleaned
    :param unit_df: a df of units
    :return: df with one-hot hacky_Smuggle hacky_Bounty columns
    """

    for ability in ['Smuggle', 'Bounty']:
        unit_df[f'hacky_{ability}'] = unit_df['ability text'].str.contains(ability).fillna(0).astype(int).copy()
    return unit_df


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
            if ability in ['Restore', 'Raid', 'Exploit']:
                value_col = unit_df['ability text'].str.lower().str.extract('[{|}]'+f"{ability.lower()}[:| ](\d+)")
            else:
                value_col = pd.Series([1 for i in range(len(unit_df))]).to_frame()
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


def do_oos_test(is_df: pd.DataFrame, oos_df: pd.DataFrame, x_cols: list, y_col: str, const: bool = False) -> None:
    is_df, results = make_fit(x_cols, y_col, is_df, const)
    is_df = calc_errors(is_df, y_col, asc=False)
    oos_x = oos_df.loc[:, x_cols]
    if const:
        oos_x = sm.add_constant(oos_x)
    oos_df.loc[:, 'predictions'] = results.predict(oos_x)
    oos_df = calc_errors(oos_df, y_col, asc=False)

    is_mean_error = is_df['error'].mean()
    is_std_error = is_df['error'].std()

    oos_mean_error = oos_df['error'].mean()
    oos_std_error = oos_df['error'].std()
    print(f'In-sample error: mean : {is_mean_error} std : {is_std_error}')
    print(f'Out-of-sample error: mean : {oos_mean_error} std : {oos_std_error}')
    t_stat, p_val, dof = ws.ttest_ind(is_df['error'], oos_df['error'])
    print(f"t-test results: t_stat {t_stat}, p_val {p_val}")


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
    d = {'total_power': total_power, 'total_hp': total_hp,
         'total_base': total_base, 'combined_total': combined_total}
    for col in d:
        unit_df.loc[unit_df.index, col] = d[col].loc[:]
    return unit_df


def make_adj_total_stats(unit_df: pd.DataFrame) -> pd.DataFrame:
    """
    makes a column  for the total stat value of a unit
    :param unit_df: a df of units
    :return:
    """
    adj_col = unit_df['power']*POWER_ADJ + unit_df['hp']
    unit_df.loc[adj_col.index, 'adj_stats'] = adj_col.copy()
    adj_col = unit_df['total_power']*POWER_ADJ + unit_df['total_hp']
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


def make_plot(unit_df: pd.DataFrame, y_col: str, x_col: str,  simple_line: bool = False) -> None:
    """
    make a plot of the results of a regression. Should probably be refactored to be more generic
    :param unit_df: df of units
    :param y_col: Y-variable
    :param x_col: X variable
    :param simple_line: Do you want to draw a simple linear fit to the data
    :return:
    """
    with plt.xkcd():
        plt.clf()
        plt.plot(unit_df[x_col], unit_df[y_col], color='r', marker='o',
                 linestyle='None', label=f'Observed {y_col}')
        plt.plot(unit_df[x_col], unit_df.predictions, color='b', marker='o',
                 linestyle='None', label=f'Predicted {y_col}')
        if simple_line:
            coef, intercept = make_simple_linear_fit(unit_df, y_col, x_col)
            simple_line_y = []
            simple_line_x = []
            for i in range(0, int(unit_df[x_col].max())+1):
                simple_line_x.append(i)
                simple_line_y.append(intercept + coef*i)
            plt.plot(simple_line_x, simple_line_y, 'k-', label='Simple Linear Fit')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend()
        plt.show()


def make_feature_plot(unit_df: pd.DataFrame, y_col: str, x_col: str, feature_column: str,
                      simple_line: bool = False) -> None:
    """
    make a plot of the results of a regression splitting out points with different features.
    Should probably be refactored to be more generic
    :param unit_df: df of units
    :param y_col: Y-variable
    :param x_col: X variable
    :param feature_column: the feature we want to highlight
    :param simple_line: Do you want to draw a simple linear fit to the data
    :return:
    """

    with plt.xkcd():

        plt.clf()
        for elem in unit_df[feature_column].unique():
            sample = unit_df.loc[unit_df[feature_column] == elem]
            plt.plot(sample[x_col], sample[y_col], marker='o',
                     linestyle='None', label=f'Observed {y_col} {feature_column}: {elem}')
        plt.plot(unit_df[x_col], unit_df.predictions, color='b', marker='o',
                 linestyle='None', label=f'Predicted {y_col}')
        if simple_line:
            coef, intercept = make_simple_linear_fit(unit_df, y_col, x_col)
            simple_line_y = []
            simple_line_x = []
            for i in range(0, int(unit_df[x_col].max())+1):
                simple_line_x.append(i)
                simple_line_y.append(intercept + coef*i)
            plt.plot(simple_line_x, simple_line_y, 'k-', label='Simple Linear Fit')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend()
        plt.show()


def make_simple_linear_fit(unit_df: pd.DataFrame, y_col: str, x_col:str) -> tuple:
    """
    make a simple linear fit (Y = mX + b) and return the m and b
    :param unit_df: a df of units
    :param y_col: the target column
    :param x_col: our variable
    :return: (m,b) from Y = mX +b
    """
    X = unit_df[x_col]
    y = unit_df[y_col]
    X = sm.add_constant(X)
    results = sm.OLS(y, X).fit()
    print(results.summary())
    m = results.params[x_col]
    b = results.params['const']
    return m, b


def calc_errors(unit_df: pd.DataFrame, y_col: str, asc=False) -> pd.DataFrame:
    unit_df.loc[unit_df.index, 'error'] = (unit_df[y_col] - unit_df['predictions']).copy()
    print(unit_df.sort_values('error', ascending=asc)[['name', 'title' , y_col, 'predictions', 'error']].head(10))

    unit_df.loc[:, 'percent_error'] = ((unit_df[y_col] - unit_df['predictions'])/unit_df[y_col]).copy()
    print(unit_df.sort_values('percent_error', ascending=asc)[['name', y_col, 'predictions', 'percent_error']].head(10))
    return unit_df


def make_qq(fit):
    with plt.xkcd():
        res = fit.resid  # residuals
        sm.qqplot(res)
        plt.show()


def make_error_histo(fit):
    with plt.xkcd():
        res = fit.resid
        plt.hist(res, bins=[-6+.5*i for i in range(24)])
        plt.title("Error Histogram")
        plt.ylabel("Number of Occurances")
        plt.xlabel("Error")
        plt.show()
