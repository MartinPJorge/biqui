import os
import pandas as pd
import numpy as np
import sys

def avg_delay(df):
    # df = cdfs[rho,c]
    # https://stats.stackexchange.com/a/13377
    # Riemman sum w/ dx=x[1]-x[0]
    dx = df['sojourn_time'].values[1] - df['sojourn_time'].values[0]
    return sum(1-df['percentile'].values) * dx


src_folder = "../results/biqui_infocom2024"
src_folder = "../results/sigmetrics2024"
mgk_folder = "../results/cdf-simu"

csv_files = [file for file in os.listdir(src_folder) if file.endswith('.csv')]
previous_folder = "04.CDFS_SOJOURN"
output_folder = "001.MGK_TOTAL_DELAY"

#previous_folder = "../results/sigmetrics2024"
output_folder = "../results/sigmetrics2024/mgk-ed"


# List of considered percentiles
percentiles = list(np.arange(0,.96, .05)) + [.99,.999,.9999,.99999]



#sys.exit(1)


# Read the original CSV file
for csv_file in filter(lambda f: '18-49-0-x1.45' in f or '18-22-0-x1.45' in f, csv_files):
    data = pd.read_csv(src_folder + '/' + csv_file, sep=' ')

    # Convert relevant columns to numeric type, and filter out non-numeric rows
    numeric_columns = ['lambda', 'z', 'ce', 'cc', 'mu', 'edge_d', 'cloud_d']
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
    data = data.dropna()

    data = data[(data['ce'] > 0) & (data['cc'] > 0) & (data['z'] > 0) & (data['z'] < 1)]

    # # Calculate rho_e and rho_c for each row
    data['rho_e'] = (data['lambda'] * (1 - data['z'])) / (data['mu'] * data['ce'])
    data['rho_c'] = (data['lambda'] * data['z']) / (data['mu'] * data['cc'])

    data = data[data['rho_e'] <= 0.95]
    data = data[data['rho_c'] <= 0.95]
    data.reset_index(drop=True, inplace=True)
    print(data)

    row_index = 0
    total_del_edge = {p: [] for p in percentiles}
    total_del_cloud = {p: [] for p in percentiles}
    avg_del_edge = []
    avg_del_cloud = []
    lambdas_ = []
    zetas_ = []
    ces_ = []
    ccs_ = []
    costs_ = []
    for row_index in range(len(data)):
        rho_e_value = data.loc[row_index, 'rho_e']
        rho_c_value = data.loc[row_index, 'rho_c']
        ce_value = data.loc[row_index, 'ce']
        cc_value = data.loc[row_index, 'cc']
        cost_value = data.loc[row_index, 'cost']
        edge_d = data.loc[row_index, 'edge_d']
        cloud_d = data.loc[row_index, 'cloud_d']
        lambda_ = data.loc[row_index, 'lambda']
        z = data.loc[row_index, 'z']
        lambdas_.append(lambda_)
        zetas_.append(z)
        ces_.append(ce_value)
        ccs_.append(cc_value)
        costs_.append(cost_value)

        # Construct the corresponding CSV file name
        file_edge  = mgk_folder + f"/rho-{rho_e_value:.2f}_c-{round(ce_value)}.csv"
        file_cloud = mgk_folder + f"/rho-{rho_c_value:.2f}_c-{round(cc_value)}.csv"



        # # # Read the corresponding CSV file
        rho_data_edge = pd.read_csv(file_edge,names=['sojourn_time', 'percentile'], header=None)
        rho_data_cloud = pd.read_csv(file_cloud,names=['sojourn_time', 'percentile'], header=None)

        # # # # # Get the sojourn time for the desired percentile (e.g., 99.999)
        for percentile_value in percentiles:
            delay_edge = rho_data_edge[rho_data_edge['percentile']<=percentile_value].tail(1)['sojourn_time'].values[0]
            delay_cloud = rho_data_cloud[rho_data_cloud['percentile']<=percentile_value].tail(1)['sojourn_time'].values[0]
            
            # Store the percentile sojourn time (w/ propagation included)
            total_del_edge[percentile_value].append(delay_edge + edge_d)
            total_del_cloud[percentile_value].append(delay_cloud + cloud_d)

        # Compute the average sojourn time (w/ propagation included)
        avg_del_edge.append(avg_delay(rho_data_edge) + edge_d)
        avg_del_cloud.append(avg_delay(rho_data_cloud) + cloud_d)


        # Create the dictionary to store
        store_dict = {
            'lambda': lambdas_,
            'z': zetas_,
            'ce': ces_,
            'cc': ccs_,
            'cost': costs_,
            'edge_avg': avg_del_edge,
            'cloud_avg': avg_del_cloud
        }
        for k,v in total_del_edge.items():
            store_dict[f'edge_{k}'] = v
        for k,v in total_del_cloud.items():
            store_dict[f'cloud_{k}'] = v


        output_file = os.path.join(output_folder, f"mgk-total-delay-{csv_file}")

        # Create the folder if it does not exist
        os.makedirs(output_folder, exist_ok=True)

        #Save total_delay_edge and total_delay_cloud to separate CSV files
        pd.DataFrame(store_dict).to_csv(output_file, index=False,
                sep=' ')

