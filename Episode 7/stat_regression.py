from regressor import *

df = read_csv('../data/cards_export_20241017b.csv')
unit_df = get_units(df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique]:
    unit_df = operation(unit_df)

X_cols = total_stat_features + ['invisibledamage', 'invisibledraw']
unit_df, results = make_fit(x_cols=X_cols, y_col='cost', unit_df=unit_df, const=False)
make_plot(unit_df, 'cost', 'combined_total')
make_qq(results)