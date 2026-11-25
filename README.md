# System Security Projects

Three Python projects from a university course on system security:

| Folder | Project | Topic |
|---|---|---|
| [`anomaly-ids/`](anomaly-ids/) | Anomaly-based intrusion detection system | statistical baselines, weighted Z-score alerts |
| [`rainbow-table/`](rainbow-table/) | MD5 rainbow table generator and lookup | password hashing, hash-reduction chains |
| [`malware-model-graph/`](malware-model-graph/) | Malware vs. defender spread model | visualising infection and neutralisation over time |

All three need Python 3. Only `malware-model-graph` needs extra packages (`numpy`, `matplotlib`).

---

## 1. Anomaly-based intrusion detection system

*Group project (3 members).*

A host-based IDS that learns what "normal" daily user activity looks like and flags days that deviate too far from it.

### How it works

1. **Initial input**: reads event definitions from `Events.txt` and expected statistics from `Stats.txt`, then checks the two files for inconsistencies:
   - an event missing from either file
   - a discrete event with a non-integer mean
   - a mean outside the event's min/max range
   - a non-positive standard deviation
2. **Activity engine**: simulates N days of activity. Each event's daily value is drawn from a Gaussian with the given mean and standard deviation. Discrete events are rounded to integers, continuous events to 2 decimals, and every value is clipped to the event's min/max.
3. **Analysis engine**: reads the generated log back, computes a baseline mean and sample standard deviation (N − 1) for each event, and writes them to `baseline_stats.txt` in the same format as `Stats.txt`.
4. **Alert engine**: given a new stats file that represents "live" behaviour, simulates live days and scores each day against the baseline:

   ```
   anomaly score = Σ  weight × |value − baseline mean| / baseline std dev
   threshold     = 2 × Σ weights
   ```

   A day is **FLAGGED** if its score is at or above the threshold, otherwise **OKAY**.

### Input formats

`Events.txt`: first line is the number of events, then `name:type:min:max:weight:`. Type is `C` (continuous) or `D` (discrete). An empty min or max means unbounded.

```
5
Logins:D:0::2:
Time online:C:0:1440:3:
...
```

`Stats.txt`: first line is the number of events, then `name:mean:std_dev:`.

```
5
Logins:4:1.5:
Time online:150.5:25.00:
...
```

### Running

```bash
cd anomaly-ids
python ids.py Events.txt Stats.txt 5
```

`5` is the number of baseline days to generate. Any positive integer works. The program then opens an interactive menu: choose `1`, give a stats file (for example `Stats.txt`) and a number of days to simulate, then read the per-day report.

```
Anomaly Threshold: 18.00
----------------------------------------
DAY   | SCORE      | STATUS
----------------------------------------
1     | 9.68       | OKAY
2     | 7.79       | OKAY
...
```

### Output files

| File | Written by | Contents |
|---|---|---|
| `activity_log.txt` | activity engine | simulated baseline days |
| `baseline_stats.txt` | analysis engine | learned mean and std dev per event |
| `live_data.txt` | alert engine | simulated live days that get scored |

---

## 2. MD5 rainbow table

A rainbow table generator and lookup tool for MD5. It shows how precomputed hash-reduction chains trade storage for lookup time when recovering passwords from their hashes.

### How it works

- **Chains**: each unused word in the password list starts a chain of length 5, alternating MD5 hashing and reduction: `word → hash → reduce → word → hash → …`. Only the start word and the final hash are stored. Words that appear inside a chain are marked as used, so they do not start new chains.
- **Reduction function**: maps a hash back to a word in the dictionary. At step *i* it takes 8 hex characters of the hash (starting at offset `(i × 8) mod 24`), converts them to an integer, and uses that number modulo the list size as an index into the password list. Using a different slice at each step keeps chains from merging as quickly.
- **Table**: entries are sorted by final hash and saved to `Rainbow.txt` as `start_word:final_hash`.
- **Lookup**: for a target hash, the tool first checks it against the final hashes. If there is no match, it re-applies reduce-and-hash from each possible chain position, looking for a final hash. When one matches, it rebuilds that chain from its start word to recover the pre-image.

### Running

`Passwords.txt` should be a word list with one candidate password per line. It is not included here.

```bash
cd rainbow-table
python Rainbow.py Passwords.txt
```

- Enter `y` to build a new table (writes `Rainbow.txt`), or `n` to load an existing one.
- Paste any 32-character MD5 hash to look up its pre-image.
- Type `quit` to exit.

Example run with a 25,143-word list: the generated table has **10,586 chains**.

```
Enter MD5 hash to find pre-image: 0010c6d8214b2e0dbcce46f52cca3734
Searching for pre-image of: 0010c6d8214b2e0dbcce46f52cca3734
Found direct match in rainbow table!

*** Pre-image found: despite ***
```

---

## 3. Malware vs. defender spread model

A matplotlib plot of a scenario in which a self-spreading AI malware **M** is countered by an AI defender **D**, over hours t = 0 to 15:

- **M (potential growth)**: infected systems grow by 10% every 2 hours if nothing stops them.
- **D (neutralisation rate)**: deployed at t = 6 and doubles its rate every 3 hours.
- **M after defence**: the malware is fully neutralised at t = 7.

The figure marks when D is deployed, when M is neutralised, and the points where D's rate doubles.

```bash
pip install numpy matplotlib
cd malware-model-graph
python CSCI262-A2-Graph.py
```
