from Reused.regressor import *


df1 = read_csv('../data/JTL Complete - card_export_2025_0506.csv')
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

make_plot(unit_df, y, 'total_power', simple_line=True)

make_error_histo(results)

unit_df = calc_errors(unit_df, y_col=y, asc=True)
make_qq(results)


#y = 'adj_stats'
#X_cols = (sqrt_features + ['invisibledraw', 'uniqueness'] + SOLID_ABILITIES +
#          ['Makes_Droids','Makes_Clones','Makes_Ties','Ramps','Makes_X_Wings', 'Indirect'] +['set_TWI'] +
#          ['invisiblepower', 'invisiblehp'])

#unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)
#
#make_plot(unit_df, y, 'cost', simple_line=True)

#make_error_histo(results)

#unit_df = calc_errors(unit_df, y_col=y, asc=False)
#make_qq(results)