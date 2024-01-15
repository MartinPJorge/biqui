import glob
import pandas as pd

def avg_delay(df):
    # df: dataframe with [x,cdf] columns

    # https://stats.stackexchange.com/a/13377
    # Riemman sum w/ dx=x[1]-x[0]
    dx = df['x'].values[1] - df['x'].values[0]
    return sum(1-df['cdf'].values) * dx

if __name__ == '__main__':
    cols = ['x', 'cdf']
    for f in glob.glob('../results/MGkapprox/cdf-sweep/*'):
        df = pd.read_csv(f, header=None).dropna()
        df.columns = cols

        avg = avg_delay(df)
        df_mock = pd.DataFrame.from_dict(
            {
                'x': [0,avg,10000000000000],
                'perc': [0, 0.99999, 1]
            }
        )

        fs = f.split('/')[-1]
        df_mock.to_csv(f'../results/MGkapprox/avg-mock-cdf/{fs}',
                index=False, header=None)

        print(f)
        print(avg)


