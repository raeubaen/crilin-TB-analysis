import os
import re
import csv

pattern = re.compile(r"result_x_(-?\d+)_y_(-?\d+)_z_(-?\d+)\.csv")

# ----------------------------
# LOAD REFERENCE
# ----------------------------
ref_map = {}


with open("intercalib_mc.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:
        try:
            x = int(row["x"])
            y = int(row["y"])
            z = int(row["z"])

            # optional coefficient
            coeff = float(row["coeff"]) if "coeff" in row else 1.0

            ref_map[(x, y, z)] = coeff
        except:
            continue


# ----------------------------
# PROCESS FILES
# ----------------------------
rows = []

for fname in os.listdir("."):
    print("\n\n new line \n\n")
    m = pattern.fullmatch(fname.strip())
    if not m:
        #print(fname, "failed")
        continue


    x, y, z = map(int, m.groups())

    print(x, y, z)

    intercalib = 1  # default

    # open result file
    try:
        with open(fname) as f:
            reader = csv.DictReader(f)

            first = next(reader, None)

            if first is not None:
                alpha = float(first["alpha"])
                print(x, y, z, alpha)
                intercalib = alpha
                if (x, y, z) in ref_map:
                    print("(x, y, z) in ref_map")
                else:
                    print("not in ref map")
                    intercalib = 1

    except Exception as e:
        print("failed:", fname, e)
        continue

    rows.append((x, y, z, intercalib))


rows.sort()

with open("output.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["x", "y", "z", "intercalib"])
    w.writerows(rows)

print("done")
