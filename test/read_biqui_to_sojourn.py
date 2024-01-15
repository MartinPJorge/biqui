import os
import pandas as pd
import numpy as np

csv_files = [file for file in os.listdir('.') if file.endswith('.csv')]
previous_folder = "04.CDFS_SOJOURN"
output_folder = "001.MGK_TOTAL_DELAY"


# Read the original CSV file
for csv_file in csv_files:
    print(csv_file)
    data = pd.read_csv(csv_file, sep=' ')

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
    total_del_edge = []
    total_del_cloud = []
    lambdas_ = []
    zetas_ = []
    ces_ = []
    ccs_ = []
    for row_index in range(len(data)):
        rho_e_value = data.loc[row_index, 'rho_e']
        rho_c_value = data.loc[row_index, 'rho_c']
        ce_value = data.loc[row_index, 'ce']
        cc_value = data.loc[row_index, 'cc']
        edge_d = data.loc[row_index, 'edge_d']
        cloud_d = data.loc[row_index, 'cloud_d']
        lambda_ = data.loc[row_index, 'lambda']
        z = data.loc[row_index, 'z']
        lambdas_.append(lambda_)
        zetas_.append(z)
        ces_.append(ce_value)
        ccs_.append(cc_value)

        # Construct the corresponding CSV file name
        if rho_e_value or rho_c_value in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90):
            file_edge = f"rho-{rho_e_value:.1f}_c-{round(ce_value)}.csv"
            file_cloud = f"rho-{rho_c_value:.1f}_c-{round(cc_value)}.csv"
        else:
            file_edge = f"rho-{rho_e_value:.2f}_c-{round(ce_value)}.csv"
            file_cloud = f"rho-{rho_c_value:.2f}_c-{round(cc_value)}.csv"

        current_directory = os.getcwd()

        parent_directory = os.path.dirname(current_directory)
        new_parent_directory = os.path.join(parent_directory, previous_folder)

        rho_csv_file_edge = os.path.join(new_parent_directory, file_edge)
        rho_csv_file_cloud = os.path.join(new_parent_directory, file_cloud)


        # # # Read the corresponding CSV file
        rho_data_edge = pd.read_csv(rho_csv_file_edge,names=['sojourn_time', 'percentile'], header=None)
        rho_data_cloud = pd.read_csv(rho_csv_file_cloud,names=['sojourn_time', 'percentile'], header=None)

        # # # # # Get the sojourn time for the desired percentile (e.g., 99.999)
        percentile_value = 0.99999
        delay_edge = rho_data_edge[rho_data_edge['percentile']<=percentile_value].tail(1)['sojourn_time'].values[0]
        delay_cloud = rho_data_cloud[rho_data_cloud['percentile']<=percentile_value].tail(1)['sojourn_time'].values[0]

        # # # # calculate total delay for edge and cloud
        total_delay_edge = delay_edge + edge_d
        total_del_edge.append(total_delay_edge)
        total_delay_cloud = delay_edge + cloud_d
        total_del_cloud.append(total_delay_cloud)

        output_file = os.path.join(output_folder, f"mgk-total-delay-{csv_file}")

        # Create the folder if it does not exist
        os.makedirs(output_folder, exist_ok=True)

        #Save total_delay_edge and total_delay_cloud to separate CSV files
        pd.DataFrame({
                    'lambda': lambdas_,
                    'z': zetas_,
                    'ce': ces_,
                    'cc': ccs_,
                    'total_delay_edge': total_del_edge,
                    'total_delay_cloud': total_del_cloud}).to_csv(output_file, index=False)

