import sys
import random
import math
import os


# 1. DATA CLASSES
class Event:
    def __init__(self, name, event_type, min_val, max_val, weight):
        self.name = name
        self.type = event_type.strip().upper()
        self.min_val = min_val if min_val is not None else 0.0
        self.max_val = max_val if max_val is not None else float('inf')
        self.weight = weight

    def __str__(self):
        max_str = f"{self.max_val:.2f}" if self.max_val != float('inf') else "Inf"
        return f"Event: {self.name} | Type: {self.type} | Range: [{self.min_val}, {max_str}] | Weight: {self.weight}"

class EventStats:
    def __init__(self, name, mean, std_dev):
        self.name = name
        self.mean = mean
        self.std_dev = std_dev

    def __str__(self):
        return f"Mean: {self.mean} | Std Dev: {self.std_dev}"

# 2. FILE PARSING
def parse_events(file_path):
    events = {}
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            print(f"Error: {file_path} is empty.")
            sys.exit(1)

        try:
            num_events = int(lines[0])
        except ValueError:
            print(f"Error: First line of {file_path} must be an integer count.")
            sys.exit(1)

        for i, line in enumerate(lines[1:], start=2):
            try:
                parts = line.split(':')
                if len(parts) < 5:
                    raise ValueError("Not enough fields")

                name = parts[0].strip()
                event_type = parts[1].strip()

                min_str = parts[2].strip()
                max_str = parts[3].strip()
                min_v = float(min_str) if min_str else None
                max_v = float(max_str) if max_str else None

                try:
                    weight = int(parts[4].strip())
                except ValueError:
                    raise ValueError(f"Invalid weight '{parts[4]}'")

                if event_type not in ('C', 'D'):
                    raise ValueError(f"Invalid event type '{event_type}'. Must be 'C' or 'D'.")

                if weight <= 0:
                    raise ValueError("Weight must be a positive integer.")

                events[name] = Event(name, event_type, min_v, max_v, weight)

            except Exception as e:
                raise ValueError(f"ERROR parsing Events.txt line {i} ('{line}'): {e}")

        if len(events) != num_events:
            print(f"WARNING: Expected {num_events} events, but parsed {len(events)}.")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    return events

def parse_stats(file_path):
    stats = {}
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            print(f"Error: {file_path} is empty.")
            sys.exit(1)

        try:
            num_stats = int(lines[0])
        except ValueError:
            print(f"Error: First line of {file_path} must be an integer count.")
            sys.exit(1)

        for i, line in enumerate(lines[1:], start=2):
            try:
                parts = line.split(':')
                if len(parts) < 3:
                    raise ValueError("Not enough fields")

                name = parts[0].strip()
                mean = float(parts[1].strip())
                std_dev = float(parts[2].strip())

                stats[name] = EventStats(name, mean, std_dev)

            except Exception as e:
                raise ValueError(f"ERROR parsing Stats.txt line {i} ('{line}'): {e}")

        if len(stats) != num_stats:
            print(f"WARNING: Expected {num_stats} statistics, but parsed {len(stats)}.")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    return stats

def check_consistency(events, stats):
    print("\n--- Consistency Check ---")
    inconsistencies = []

    event_names = set(events.keys())
    stat_names = set(stats.keys())

    missing_in_stats = event_names - stat_names
    for name in missing_in_stats:
        msg = f"Event '{name}' is defined in Events.txt but missing in Stats.txt."
        print("INCONSISTENCY:", msg)
        inconsistencies.append(msg)

    missing_in_events = stat_names - event_names
    for name in missing_in_events:
        msg = f"Statistic '{name}' appears in Stats.txt but does not exist in Events.txt."
        print("INCONSISTENCY:", msg)
        inconsistencies.append(msg)

    for name in (event_names & stat_names):
        evt = events[name]
        stat = stats[name]

        if evt.type == 'D' and not stat.mean.is_integer():
            msg = f"Discrete event '{name}' has non-integer mean ({stat.mean})."
            print("INCONSISTENCY:", msg)
            inconsistencies.append(msg)

        if stat.mean < evt.min_val:
            msg = f"Mean ({stat.mean}) for '{name}' is below minimum allowed ({evt.min_val})."
            print("INCONSISTENCY:", msg)
            inconsistencies.append(msg)

        if stat.mean > evt.max_val:
            msg = f"Mean ({stat.mean}) for '{name}' exceeds maximum allowed ({evt.max_val})."
            print("INCONSISTENCY:", msg)
            inconsistencies.append(msg)

        if stat.std_dev <= 0:
            msg = f"Standard deviation for '{name}' must be positive ({stat.std_dev})."
            print("INCONSISTENCY:", msg)
            inconsistencies.append(msg)

    if not inconsistencies:
        print("Data consistency verified.\n")
    else:
        print("\nTotal inconsistencies detected:", len(inconsistencies))

    return inconsistencies

# 3. ACTIVITY & ANALYSIS ENGINES
def generate_event_value(event, stats):
    value = random.gauss(stats.mean, stats.std_dev)

    if event.type == 'D':
        value = int(round(value))

    if value < event.min_val:
        value = event.min_val

    if value > event.max_val:
        value = event.max_val

    if event.type == 'C':
        value = round(float(value), 2)

    return value


def generate_daily_events(events, stats):
    daily_data = {}
    for name, event in events.items():
        stat = stats[name]
        value = generate_event_value(event, stat)
        daily_data[name] = value
    return daily_data


def write_logs(filename, days, events, stats):
    print(f"\n--- Generating {days} Days of Activity Logs ---")

    with open(filename, "w") as f:
        for d in range(1, days + 1):
            f.write(f"DAY {d}\n")
            daily_events = generate_daily_events(events, stats)
            for name, value in daily_events.items():
                f.write(f"{name}: {value}\n")
            f.write("---\n")

    print(f"Activity logs generated → {filename}")

def analyze_logs(log_file, events, output_stats_file):
    print(f"Processing baseline analysis: {log_file}")

    daily_totals = {name: [] for name in events}

    if not os.path.exists(log_file):
        print(f"Error: {log_file} not found.")
        return {}

    with open(log_file, 'r') as f:
        current_day_data = {}
        for line in f:
            line = line.strip()
            if not line: continue

            if line.startswith("DAY"):
                if current_day_data:
                    for name, val in current_day_data.items():
                        if name in daily_totals:
                            daily_totals[name].append(val)
                current_day_data = {}

            elif line == "---":
                if current_day_data:
                    for name, val in current_day_data.items():
                        if name in daily_totals:
                            daily_totals[name].append(val)
                current_day_data = {}

            elif ':' in line:
                parts = line.split(':')
                name = parts[0].strip()
                try:
                    val = float(parts[1].strip())
                    current_day_data[name] = val
                except ValueError:
                    continue

        if current_day_data:
            for name, val in current_day_data.items():
                if name in daily_totals:
                    daily_totals[name].append(val)

    new_stats = {}
    with open(output_stats_file, 'w') as f:
        f.write(f"{len(events)}\n")
        for name, data in daily_totals.items():
            if not data: continue

            n = len(data)
            mean = sum(data) / n

            if n > 1:
                variance = sum((x - mean) ** 2 for x in data) / (n - 1)
                std_dev = math.sqrt(variance)
            else:
                std_dev = 0.0

            mean = round(mean, 2)
            std_dev = round(std_dev, 2)

            new_stats[name] = EventStats(name, mean, std_dev)
            f.write(f"{name}:{mean}:{std_dev}:\n")

    print(f"Baseline statistics saved to {output_stats_file}")
    return new_stats


# 4. ALERT ENGINE
def alert_engine(events, baseline_stats):
    while True:
        print("\n[Alert Engine] Options: [1] Run Simulation, [2] Quit")
        choice = input("Enter choice: ").strip()

        if choice == '2':
            break
        if choice != '1':
            continue

        new_file = input("Enter stats file (e.g., Stats.txt): ").strip()
        if not os.path.exists(new_file):
            print("Error: File not found.")
            continue

        try:
            days_str = input("Days to simulate: ")
            days = int(days_str)
        except ValueError:
            print("Error: Invalid integer.")
            continue

        try:
            live_stats = parse_stats(new_file)
        except SystemExit:
            continue

        live_log = "live_data.txt"
        write_logs(live_log, days, events, live_stats)

        sum_weights = sum(e.weight for e in events.values())
        threshold = 2 * sum_weights

        print(f"\nAnomaly Threshold: {threshold:.2f}")
        print("-" * 40)
        print(f"{'DAY':<5} | {'SCORE':<10} | {'STATUS':<10}")
        print("-" * 40)

        current_day_vals = {}
        day_count = 0

        with open(live_log, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue

                if line.startswith("DAY"):
                    day_count += 1
                    current_day_vals = {}
                elif line == "---":
                    anomaly_score = 0.0
                    for name, val in current_day_vals.items():
                        base = baseline_stats.get(name)
                        evt = events.get(name)

                        if base and evt:
                            sd = base.std_dev if base.std_dev > 0.001 else 0.001
                            deviation = abs(val - base.mean) / sd
                            weighted_deviation = deviation * evt.weight
                            anomaly_score += weighted_deviation

                    status = "FLAGGED" if anomaly_score >= threshold else "OKAY"
                    print(f"{day_count:<5} | {anomaly_score:<10.2f} | {status:<10}")
                    current_day_vals = {}

                elif ':' in line:
                    p = line.split(':')
                    if len(p) >= 2:
                        try:
                            current_day_vals[p[0].strip()] = float(p[1].strip())
                        except ValueError:
                            pass


# 5. MAIN ENTRY POINT
def main():
    if len(sys.argv) < 4:
        print("Usage: python ids.py Events.txt Stats.txt <Days>")
        return

    events_file = sys.argv[1]
    stats_file = sys.argv[2]
    try:
        days = int(sys.argv[3])
        if days <= 0:
            raise ValueError
    except ValueError:
        print("Error: Days must be a positive integer.")
        return

    print("=== IDS System Started ===")
    events = parse_events(events_file)
    stats = parse_stats(stats_file)
    check_consistency(events, stats)

    print("\n--- FINAL LOADED EVENT/STATISTICS REPORT ---")
    for name, event in events.items():
        stat_str = str(stats[name]) if name in stats else "NO STATS FOUND"
        print(f"{event} | {stat_str}")

    baseline_log = "activity_log.txt"
    write_logs(baseline_log, days, events, stats)

    baseline_stats_file = "baseline_stats.txt"
    new_baseline = analyze_logs(baseline_log, events, baseline_stats_file)

    if new_baseline:
        alert_engine(events, new_baseline)
    else:
        print("Error: Could not calculate baseline.")

    print("\n=== IDS System Complete ===")


if __name__ == "__main__":
    main()