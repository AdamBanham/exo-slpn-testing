import matplotlib.pyplot as plt
import numpy as np

from sys import argv

if (len(argv) < 2):
    print("Usage: python visualise.py <file>")
    exit()  
print(argv)
file = argv[1]
file_prefix = file.split(".")[0]

MQ_DEG = 2
RUN_DEG = 1 
MEM_DEG = 5


# Read data from file
data = []
with open(file, "r") as file:
    for line in file:
        y = line.strip().split('[Measures]')[1]
        y = y.split("[Timing]")[0]
        y = eval(y)
        x = line.strip().split('[Measures]')[0].split('[Config]')[1]
        x = eval(x)
        z = line.strip().split('[Measures]')[1]
        z = z.split("[Timing]")[1]
        z = eval(z)
        print(x)
        if 'type' in x:
            x['type'] = x['type'].split(".")[-1].replace("SLPNEDDiscovery","")
        else:
            x['type'] = x['minerType'].split(".")[-1].replace("SLPNEDDiscovery","")
        data.append((x['samples'], y['edEMSu'], x['type'], z['disc'], y['disc-mem']))

# Plot the data
fig = plt.figure(figsize=(20,5))
axes = fig.subplots(1,3,width_ratios=[0.8,0.8,0.8])
ax = axes[0]
labels = sorted(list(set(([ l for _, _, l,_,_ in data]))))
colors = plt.cm.get_cmap('tab10')
cmapper = {label: colors(i) for i, label in enumerate(labels)}
samples = sorted(list(set([x for x, _, _,_,_ in data])))
pairwise = dict(
    (label, 0) for label in labels
)
# compute pairwise comparisions
for s in samples:
    subdata =[(x, y, l) for x, y, l,_,_ in data if x == s]
    for tech in labels:
        ldata = [ y for x, y, l in subdata if l == tech] 
        odata = [ y for x, y, l in subdata if l != tech]
        for mes in ldata:
            pairwise[tech] += len([ y for y in odata if mes > y])

max_y = 0
for label in labels:
    subdata = sorted([(x, y) for x, y, l,_,_ in data if l == label], key=lambda x: x[0])
    # Compute the line of best fit
    x_values = [x for x, _ in subdata]
    y_values = [y for _, y in subdata]
    coefficients = np.polyfit(x_values, y_values, MQ_DEG)
    polynomial = np.poly1d(coefficients)
    y_fit = polynomial(x_values)
    ax.plot(x_values, y_fit, label=f"{label}", color=cmapper[label])
    # Calculate the confidence intervals
    p = polynomial
    y_hat = p(x_values)
    y_bar = np.mean(y_values)
    ss_reg = np.sum((y_hat - y_bar) ** 2)
    ss_tot = np.sum((y_values - y_bar) ** 2)
    r2 = ss_reg / ss_tot
    n = len(y_values)
    t = 1.96  # 95% confidence interval
    s_err = np.sqrt(np.sum((y_values - y_hat) ** 2) / (n - 2))
    confs = t * s_err * np.sqrt(1/n + (x_values - np.mean(x_values))**2 / np.sum((x_values - np.mean(x_values))**2))
    ax.fill_between(x_values, y_fit - confs, y_fit + confs, color=cmapper[label], alpha=0.2)
    # show scatter results
    ax.plot(x_values, y_values,"o",label=label,color=cmapper[label], alpha=0.18)
    max_y = max(max_y, max(y_values))
ax.set_title(f"Pairwise Comparisions: {str(pairwise)}",{"fontsize":8})
ax.legend()
ax.set_ylim(bottom=0, top=0.2)
ax.set_ylabel("edEMSu")
ax.set_xlabel("Number of Samples")
ax = axes[1]
for label in labels:
    subdata = sorted([(x, y) for x, _, l,y,_ in data if l == label], key=lambda x: x[0])
    # Compute the line of best fit
    x_values = [x for x, _ in subdata]
    y_values = [y for _, y in subdata]
    coefficients = np.polyfit(x_values, y_values, RUN_DEG)
    polynomial = np.poly1d(coefficients)
    y_fit = polynomial(x_values)
    ax.plot(x_values, y_fit, label=f"{label}", color=cmapper[label])
    # Calculate the confidence intervals
    p = polynomial
    y_hat = p(x_values)
    y_bar = np.mean(y_values)
    ss_reg = np.sum((y_hat - y_bar) ** 2)
    ss_tot = np.sum((y_values - y_bar) ** 2)
    r2 = ss_reg / ss_tot
    n = len(y_values)
    t = 1.96  # 95% confidence interval
    s_err = np.sqrt(np.sum((y_values - y_hat) ** 2) / (n - 2))
    confs = t * s_err * np.sqrt(1/n + (x_values - np.mean(x_values))**2 / np.sum((x_values - np.mean(x_values))**2))
    ax.fill_between(x_values, y_fit - confs, y_fit + confs, color=cmapper[label], alpha=0.2)
    # show scatter results
    ax.plot(x_values, y_values,"o",label=label,color=cmapper[label], alpha=0.18)
ax.legend()
ax.set_ylim(bottom=0)
ax.set_ylabel("Discovery Time (ms)")
ax.set_xlabel("Number of Samples")
ax = axes[2]
for label in labels:
    subdata = sorted([(x, y) for x, _, l,_,y in data if l == label], key=lambda x: x[0])
    # Compute the line of best fit
    x_values = [x for x, _ in subdata]
    y_values = [y for _, y in subdata]
    coefficients = np.polyfit(x_values, y_values, MEM_DEG)
    polynomial = np.poly1d(coefficients)
    y_fit = polynomial(x_values)
    ax.plot(x_values, y_fit, label=f"{label}", color=cmapper[label])
    # Calculate the confidence intervals
    p = polynomial
    y_hat = p(x_values)
    y_bar = np.mean(y_values)
    ss_reg = np.sum((y_hat - y_bar) ** 2)
    ss_tot = np.sum((y_values - y_bar) ** 2)
    r2 = ss_reg / ss_tot
    n = len(y_values)
    t = 1.96  # 95% confidence interval
    s_err = np.sqrt(np.sum((y_values - y_hat) ** 2) / (n - 2))
    confs = t * s_err * np.sqrt(1/n + (x_values - np.mean(x_values))**2 / np.sum((x_values - np.mean(x_values))**2))
    ax.fill_between(x_values, y_fit - confs, y_fit + confs, color=cmapper[label], alpha=0.2)
    # show scatter results
    ax.plot(x_values, y_values,"o",label=label,color=cmapper[label], alpha=0.18)
ax.legend()
ax.set_ylim(bottom=0)
ax.set_ylabel("Memory Usage (MB)")
ax.set_xlabel("Number of Samples")
fig.suptitle(f"SLPNEDDiscovery using road fines")

# before showing save out files
fig.savefig(f"{file_prefix}.png",dpi=300,transparent=True)
fig.savefig(f"{file_prefix}.svg",dpi=300,transparent=True)
fig.savefig(f"{file_prefix}.eps",dpi=300,transparent=True)

plt.show()