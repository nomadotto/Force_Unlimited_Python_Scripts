import matplotlib.pyplot as plt
import pandas as pd

from Reused.regressor import *
import numpy as np

df = read_csv('../data/card_data_SHD_complete - Adjusted.csv')
unit_df = get_units(df)
unit_df = unit_df[unit_df.set != 'TWI']
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique, make_set_features,
                  make_hacky_smuggle_bounty, make_rarity_feature]:
    unit_df = operation(unit_df)
y = 'adj_total_stats'
X_cols = sqr_features + ['rarity', 'invisibledamage', 'invisibledraw'] + SOLID_ABILITIES
unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)
unit_df.loc[unit_df.index, 'error'] = (unit_df[y] - unit_df['predictions']).copy()

best_units_df = pd.DataFrame(columns=['name', y, 'predictions', 'error'])
for cost in range(1,10):
    cost_df = unit_df[unit_df.cost == cost]
    cost_row = cost_df.sort_values('error', ascending=False)[['name', y, 'predictions', 'error']].head(1)
    best_units_df = pd.concat([best_units_df, cost_row], ignore_index=True)

print(best_units_df)