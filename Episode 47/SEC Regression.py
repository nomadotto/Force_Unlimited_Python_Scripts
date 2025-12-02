import numpy as np

from Reused.regressor import *


df1 = read_csv('../data/SEC Card Data - Sheet1.csv')
sec_df = df1[df1.set.isin(['JTL', 'TWI', 'SOR', 'SHD', 'LOF', 'SEC'])]


unit_df = get_units(sec_df)
for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_unconditional_ability_features, make_conditional_ability_features, make_aspect_features,
                  count_aspects, make_unique, make_set_features, make_hacky_smuggle_bounty, make_rarity_feature,
                  make_trait_features, make_is_expensive_feature, make_is_big_feature,
                  make_is_cheap_feature, make_is_double_aspect_feature]:
    unit_df = operation(unit_df)

y = 'cost'
X_cols = (simple_stat_features + ['invisibledamage', 'invisibledraw', 'uniqueness'] + SOLID_COST_ABILITIES +
          rarity_features + ['droid', 'Heals', 'is_big', 'n_aspects', 'Bounce',	'Cannot_Attack'] +
          ['Makes_Spies','Disclose_Symbols', 'Plot', 'Exhaust',	'Capture', 'Smuggle', 'set_SEC'])

unit_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=unit_df, const=True)

#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['SOR'])
#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['LOF'])
#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['TWI'])
#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['IBH'])
#make_plot(unit_df, y, 'total_base', simple_line=True)
make_error_histo(results)

unit_df = calc_errors(unit_df, y_col=y, asc=True)
make_qq(results)

