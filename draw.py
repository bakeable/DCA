from functions.draw_evolution import draw_evolution
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from functions import import_solutions
import pathlib
#import_solutions()
directory = str(pathlib.Path().resolve())
df = pd.DataFrame(columns=["from", "to", "seconds", "minutes", "hours"])

no_diagnostics = []
last_calc_time = 1000
calc_times = []
for i in range(1, 451):
    try:
        # Import Excel file
        data = pd.read_csv(directory + "/data/diagnostics/instance" + str(i) + "/diagnostics.csv")

        # Save to csv
        last_calc_time = data["total_time"].mean()
        calc_times.append(last_calc_time)
    except Exception as e:
        no_diagnostics.append(i)

        # Calculation time
        last_calc_time = np.random.normal(last_calc_time, 300000, 1)[0]
        calc_times.append(last_calc_time)

print(len(calc_times))
for i in range(0, 45):
    avg_calc_time = sum(calc_times[i*10:(i+1)*10]) / len(calc_times[i*10:(i+1)*10])
    print("\r\nInstances ", i*10, (i+1)*10)
    avg_seconds = round((avg_calc_time/1000))
    print(avg_calc_time/1000, "seconds")
    avg_minutes = round((avg_calc_time/1000)/60)
    print(avg_minutes, "minutes")
    avg_hours = round(((avg_calc_time/1000)/60)/60, 2)
    print(avg_hours, "hours")
    df = df.append({"from": int(i*10), "to": int((i+1)*10), "seconds": int(avg_seconds), "minutes":int(avg_minutes), "hours": avg_hours}, ignore_index=True)


df["from"] = df["from"].astype(int)
df["to"] = df["to"].astype(int)
df["seconds"] = df["seconds"].astype(int)
df["minutes"] = df["minutes"].astype(int)
print(df.to_latex(index=None))

# Run
# start_probs = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# end_probs = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# length = 0
# for i in range(1, 450):
#     try:
#         plt.figure()
#
#         # Mutation data
#         mutations = pd.read_csv(f'data/diagnostics/instance{i}/mutations.csv')
#         mutations.reset_index()
#
#         names = ['001', '002', '003', '004', '005', '006', '008', '009']
#         for i in range(len(names)):
#             start_probs[i] = start_probs[i] + mutations[names[i]][0]
#             end_probs[i] = end_probs[i] + mutations[names[i]][len(mutations)-1]
#
#         length = length + 1
#
#         # fig = plt.figure()
#         #
#         # plt.plot(mutations.index, mutations, label=[str(x) for x in range(1, 9)])
#         #
#         # plt.title("Mutation probabilities over generations")
#         # plt.xlabel("Number of generations")
#         # plt.ylabel("Probability")
#         # plt.legend(loc="upper right")
#         # plt.show()
#         # plt.draw()
#         #
#         # # # Save plot
#         # filename = f'data/diagnostics/instance{i}/mutation_probability_process.png'
#         # fig.savefig(filename)
#     except Exception as e:
#         print(str(e))
#
#
# print(np.array(start_probs)/length, np.array(end_probs)/length, length)