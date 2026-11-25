import hashlib
import sys


class RainbowTable:
    def __init__(self):
        self.passwords = []
        self.rainbow_table = []
        self.chain_length = 5

    def load_passwords(self, filename):

        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                self.passwords = [line.strip() for line in f if line.strip()]
            print(f"Number of words read in: {len(self.passwords)}")
            return True
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

    def hash_function(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def reduction_function(self, hash_value, step):
        start_idx = (step * 8) % 24
        hex_substring = hash_value[start_idx:start_idx + 8]

        try:
            hash_int = int(hex_substring, 16)
        except ValueError:
            hash_int = 0

        index = hash_int % len(self.passwords)
        return self.passwords[index]

    def generate_rainbow_table(self):
        used_passwords = set()
        table_entries = 0

        print("Generating rainbow table...")

        for password in self.passwords:
            if password in used_passwords:
                continue

            used_passwords.add(password)
            current_word = password
            current_hash = self.hash_function(current_word)

            for step in range(self.chain_length):
                current_word = self.reduction_function(current_hash, step)
                used_passwords.add(current_word)
                current_hash = self.hash_function(current_word)

            self.rainbow_table.append((password, current_hash))
            table_entries += 1

            if table_entries % 1000 == 0:
                print(f"Generated {table_entries} chains...")

        self.rainbow_table.sort(key=lambda x: x[1])

        self.save_rainbow_table()

        print(f"Rainbow table generation complete.")
        print(f"Number of lines in rainbow table: {len(self.rainbow_table)}")

        return True

    def save_rainbow_table(self):
        try:
            with open('Rainbow.txt', 'w') as f:
                for password, final_hash in self.rainbow_table:
                    f.write(f"{password}:{final_hash}\n")
            print("Rainbow table saved to Rainbow.txt")
        except Exception as e:
            print(f"Error saving rainbow table: {e}")

    def load_rainbow_table(self):
        try:
            self.rainbow_table = []
            with open('Rainbow.txt', 'r') as f:
                for line in f:
                    if ':' in line:
                        password, final_hash = line.strip().split(':', 1)
                        self.rainbow_table.append((password, final_hash))
            print(f"Loaded {len(self.rainbow_table)} entries from Rainbow.txt")
            return True
        except FileNotFoundError:
            print("Error: Rainbow.txt not found. Please generate the table first.")
            return False

    def validate_hash(self, hash_str):
        if len(hash_str) != 32:
            return False
        try:
            int(hash_str, 16)
            return True
        except ValueError:
            return False

    def find_preimage(self, target_hash):
        print(f"Searching for pre-image of: {target_hash}")

        for original_password, final_hash in self.rainbow_table:
            if final_hash == target_hash:
                print("Found direct match in rainbow table!")
                return self.reconstruct_chain(original_password, target_hash)

        print("Direct match not found. Traversing chains...")

        for step in range(self.chain_length):
            current_hash = target_hash

            for chain_step in range(step, self.chain_length):
                current_word = self.reduction_function(current_hash, chain_step)
                current_hash = self.hash_function(current_word)

                for original_password, final_hash in self.rainbow_table:
                    if final_hash == current_hash:
                        print(f"Found chain match at step {step}!")
                        return self.reconstruct_chain_from_position(
                            original_password, target_hash, step
                        )

        return None

    def reconstruct_chain(self, start_password, target_hash):
        current_word = start_password
        current_hash = self.hash_function(current_word)

        if current_hash == target_hash:
            return start_password

        for step in range(self.chain_length):
            current_word = self.reduction_function(current_hash, step)
            current_hash = self.hash_function(current_word)

            if current_hash == target_hash:
                return current_word

        return None

    def reconstruct_chain_from_position(self, start_password, target_hash, stop_step):
        current_word = start_password
        current_hash = self.hash_function(current_word)

        if current_hash == target_hash:
            return start_password

        for step in range(self.chain_length):
            current_word = self.reduction_function(current_hash, step)
            current_hash = self.hash_function(current_word)

            if current_hash == target_hash:
                return current_word

            if step >= stop_step:
                break

        return None

    def interactive_lookup(self):
        print("\n" + "=" * 50)
        print("Rainbow Table Lookup Mode")
        print("Enter 'quit' to exit")
        print("=" * 50)

        while True:
            hash_input = input("\nEnter MD5 hash to find pre-image: ").strip()

            if hash_input.lower() == 'quit':
                break

            if not self.validate_hash(hash_input):
                print("Error: Invalid MD5 hash. Must be 32 hexadecimal characters.")
                continue

            preimage = self.find_preimage(hash_input)

            if preimage:
                print(f"\n*** Pre-image found: {preimage} ***")
            else:
                print("No pre-image found — hash not present in rainbow table.")

    def run(self, password_file):
        print("Rainbow Table Generator")
        print("=" * 40)

        if not self.load_passwords(password_file):
            return

        if len(self.passwords) == 0:
            print("Error: No passwords loaded.")
            return

        generate_new = input("Generate new rainbow table? (y/n): ").lower().startswith('y')

        if generate_new:
            if not self.generate_rainbow_table():
                return
        else:
            if not self.load_rainbow_table():
                return

        self.interactive_lookup()


def main():
    if len(sys.argv) != 2:
        print("Usage: python Rainbow.py Passwords.txt")
        sys.exit(1)

    password_file = sys.argv[1]
    rainbow = RainbowTable()
    rainbow.run(password_file)


if __name__ == "__main__":
    main()