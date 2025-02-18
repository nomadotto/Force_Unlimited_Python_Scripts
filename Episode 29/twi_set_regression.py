from Reused.regressor import *

df1 = read_csv('../data/card_data_SHD_complete - Adjusted.csv')
df1 = df1[df1['set'] != 'TWI'].reset_index()
df2 = read_csv('../data/TWI Units.csv')
df = pd.concat([df1, df2], axis = 0, ignore_index=True)
unit_df = get_units(df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique, make_set_features,
                  make_hacky_smuggle_bounty, make_rarity_feature]:
    unit_df = operation(unit_df)

# you can use adj_total_stats (adjusted stats + includes "hidden" stats) /
# adj_stats (6/5*power + HP)/
# total_base (power + HP) instead to see the difference

y = 'adj_total_stats'
X_cols = base_cost_features + ['rarity', 'invisibledamage', 'invisibledraw', 'uniqueness'] + SOLID_ABILITIES
unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)

make_plot(unit_df, y, 'cost', simple_line=True)

make_error_histo(results)

#make_feature_plot(unit_df, y, 'adj_stats', 'hacky_Bounty', simple_line=True)
unit_df = calc_errors(unit_df, y_col=y, asc=False)
make_qq(results)

