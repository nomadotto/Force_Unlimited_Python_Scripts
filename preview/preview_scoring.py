from Reused.regressor import *


df1 = read_csv('./data/JTL Complete - card_export_2025_0506.csv')
jtl_df = df1[df1.set.isin(['JTL', 'TWI', 'SOR', 'SHD'])]


unit_df = get_units(jtl_df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique, make_set_features,
                  make_hacky_smuggle_bounty, make_rarity_feature]:
    unit_df = operation(unit_df)

y = 'cost'
X_cols = (simple_stat_features + ['invisibledamage', 'invisibledraw', 'uniqueness'] + SOLID_COST_ABILITIES +
          rarity_features )


unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)


new_cards = read_csv('./data/previews.csv')

new_df = get_units(new_cards)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_ability_features, make_aspect_features, count_aspects, make_unique, make_set_features,
                  make_hacky_smuggle_bounty, make_rarity_feature]:
    new_df = operation(new_df)
new_df = new_df[new_df.set == 'LOF']
new_df = new_df[new_df.cost == 2]
new_preds = results.predict(sm.add_constant(new_df[X_cols]))
new_df['preds'] = new_preds
print(new_df.head())
new_df.to_csv('preview_prediction_results_2_cost.csv')