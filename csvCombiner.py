import numpy as np
import pandas as pd

covers = np.empty((0, 9075))
genres = pd.DataFrame()

for i in range(1, 101):
    print(i)
    try:
        sub_mtx = np.genfromtxt('covers'+str(i)+'.csv', delimiter=',')
        covers = np.append(covers, sub_mtx, axis=0)
        sub_genres = pd.read_csv('genres'+str(i)+'.csv')
        genres = pd.concat([genres, sub_genres])
    except:
        print('fail')
        continue

genres = genres.drop(genres.columns[0], axis='columns')
np.savetxt("covers.csv", covers, delimiter=",")
genres.to_csv("genres.csv")

print(covers.shape)
print(genres.size)
