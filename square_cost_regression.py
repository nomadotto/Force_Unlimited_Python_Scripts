from regressor import *

df = read_csv('data/card_data_sor_complete.csv')
unit_df = get_units(df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique]:
    unit_df = operation(unit_df)


y = 'adj_total_stats'  # you can use adj_total_stats /total_base instead to see the difference
X_cols = sqr_features + ['invisibledamage', 'invisibledraw']
unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)
make_plot(unit_df, y, 'cost')
unit_df = calc_errors(unit_df, y_col=y, asc=False)
make_qq(results)