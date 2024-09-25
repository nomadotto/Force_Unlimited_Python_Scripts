import matplotlib.pyplot as plt

from Reused.regressor import *
import numpy as np

df = read_csv('../data/card_data_SHD_complete - Adjusted.csv')
unit_df = get_units(df)
unit_df = unit_df[unit_df.set != 'TWI']
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique, make_set_features,
                  make_hacky_smuggle_bounty, make_rarity_feature]:
    unit_df = operation(unit_df)

# you can use adj_total_stats (adjusted stats + includes "hidden" stats) /
# adj_stats (6/5*power + HP)/
# total_base (power + HP) instead to see the difference

y = 'adj_total_stats'
X_cols = sqr_features + ['rarity', 'invisibledamage', 'invisibledraw'] + SOLID_ABILITIES
unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)
unit_df.loc[unit_df.index, 'error'] = (unit_df[y] - unit_df['predictions']).copy()
median_error = unit_df[['aspects', 'error']].groupby('aspects').median().sort_values('error')
mean_error = unit_df[['aspects', 'error']].groupby('aspects').mean().sort_values('error')
std_error = unit_df[['aspects','error']].groupby('aspects').std()

with plt.xkcd():
    plt.clf()
    plt.figure(figsize=(11,8.5))
    y_pos = np.arange(len(median_error.index))
    plt.barh(y_pos,median_error.values.ravel(), align='center')
    plt.yticks(y_pos,labels=median_error.index.to_list())
    plt.xlabel('Median(Adj Stats - predicted Adj Stats) ')
    plt.title('Prediction Error By Aspect')
    plt.show()

with plt.xkcd():
    plt.clf()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(mean_error.index))
    ax.barh(y_pos,mean_error.values.ravel(), align='center')
    ax.set_yticks(y_pos,labels=mean_error.index.to_list())
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('mean(Adj Stats - predicted Adj Stats) ')
    ax.set_title('Prediction Error By Aspect')
    plt.show()