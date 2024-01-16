from regressor import *

df = read_csv('data/card_export_20231209.csv')
unit_df = get_units(df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique]:
    unit_df = operation(unit_df)

X_cols = sqr_features + ['n_aspects']
unit_df, results = make_fit(x_cols=X_cols, y_col='adj_total_stats', unit_df=unit_df, const=True)
make_plot(unit_df, 'adj_total_stats', 'cost')
unit_df = calc_errors(unit_df, y_col='adj_total_stats', asc=False)
make_qq(results)