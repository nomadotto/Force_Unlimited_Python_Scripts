import numpy as np

from Reused.regressor import *


df1 = read_csv('../data/SEC Card Data - Sheet1.csv')
sec_df = df1[df1.set.isin(['JTL', 'TWI', 'SOR', 'SHD', 'LOF', 'SEC'])]


leader_df = get_leaders(sec_df)
leader_df.loc[:,'keyword_3'] = leader_df.loc[:,'keyword_3'].astype(str)
ABILITIES = ['Sentinel', 'Raid', 'Overwhelm', 'Shielded', 'Saboteur', 'Restore', 'Grit',
             'Coordinate', 'Hidden', 'Piloting']

for operation in [make_total_stats, make_adj_total_stats, make_sqrt_cost_feature, make_sqr_cost_feature,
                  make_unconditional_ability_features, make_conditional_ability_features, make_aspect_features,
                  count_aspects, make_set_features, make_rarity_feature,
                  make_trait_features, make_is_expensive_feature, make_is_big_feature,
                  make_is_cheap_feature, make_is_double_aspect_feature]:
    leader_df = operation(leader_df)

y = 'cost'
X_cols = (['power', 'hp'] + LEADER_COST_ABILITIES + ['n_aspects'])

leader_df, results = make_fit(x_cols=X_cols, y_col=y, unit_df=leader_df, const=False)

#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['SOR'])
#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['LOF'])
#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['TWI'])
#make_plot(unit_df, y, 'total_base', simple_line=True, sets = ['IBH'])
#make_plot(unit_df, y, 'total_base', simple_line=True)
make_error_histo(results)

leader_df = calc_errors(leader_df, y_col=y, asc=True)
make_qq(results)

