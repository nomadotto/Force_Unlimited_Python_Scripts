from Reused.regressor import *

df = read_csv('../data/May_27_SHD_export.csv')
unit_df = get_units(df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique, make_set_features,
                  make_hacky_smuggle_bounty]:
    unit_df = operation(unit_df)

# you can use adj_total_stats (adjusted stats + includes "hidden" stats) /
# adj_stats (6/5*power + HP)/
# total_base (power + HP) instead to see the difference

y = 'adj_stats'
X_cols = sqr_features + ['hacky_Bounty', 'hacky_Smuggle'] #['set_SHD']  #   #  #  #['hacky_Bounty'] simple_stat_features
unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)
make_feature_plot(unit_df, y, 'cost', 'hacky_Bounty', simple_line=True)
unit_df = calc_errors(unit_df, y_col=y, asc=False)
make_qq(results)

# let's do the in-sample / oos test:
X_cols = sqr_features
is_df = get_sets(unit_df, ['SOR'])
oos_df = get_sets(unit_df, ['SHD'])
do_oos_test(is_df, oos_df, x_cols=X_cols, y_col=y, const=True)