CSCI262 – Assignment 1 (Part 2)

This program implements a simple Rainbow Table Generator and Lookup Tool
using the MD5 hashing algorithm. It demonstrates how rainbow tables can be
used to find pre-images of hashes through iterative hash–reduction chains.

Main components:
- RainbowTable class
- Password list (Passwords.txt)
- Reduction function
- Hashing (MD5)
- Table generation and lookup
files require:
- Rainbow.py
- Passwords.txt

How to use:
1. Place Rainbow.py and Passwords.txt in the same folder.
2. type in cmd the command -> cd to the directory containing Rainbow.py and Passwords.txt
3. Run from terminal:
      python Rainbow.py Passwords.txt
4. When prompted:
   - Enter 'y' to generate a new Rainbow Table (Rainbow.txt will be created)
   - Enter 'n' to load an existing Rainbow.txt
5. After generation, enter any MD5 hash to find its pre-image.
6. Type 'quit' to exit the lookup mode.

Output:
C:\Users\Chong Jing Ming\Desktop\9902156_A1_PartOneAndTwo>python Rainbow.py Passwords.txt
Rainbow Table Generator
========================================
Number of words read in: 25143
Generate new rainbow table? (y/n): y
Generating rainbow table...
Generated 1000 chains...
Generated 2000 chains...
Generated 3000 chains...
Generated 4000 chains...
Generated 5000 chains...
Generated 6000 chains...
Generated 7000 chains...
Generated 8000 chains...
Generated 9000 chains...
Generated 10000 chains...
Rainbow table saved to Rainbow.txt
Rainbow table generation complete.
Number of lines in rainbow table: 10586

==================================================
Rainbow Table Lookup Mode
Enter 'quit' to exit
==================================================

Enter MD5 hash to find pre-image: 0010c6d8214b2e0dbcce46f52cca3734
Searching for pre-image of: 0010c6d8214b2e0dbcce46f52cca3734
Found direct match in rainbow table!

*** Pre-image found: despite ***

Enter MD5 hash to find pre-image: 0010c6d8214b2e0dbcce46f52cca3735
Searching for pre-image of: 0010c6d8214b2e0dbcce46f52cca3735
Direct match not found. Traversing chains...
Found chain match at step 0!
No pre-image found — hash not present in rainbow table.

Enter MD5 hash to find pre-image:

Description of how i do the reduction:
The reduction function maps an MD5 hash back into a possible plaintext password from the dictionary.
In the program (Rainbow.py), it is implemented as:

    def reduction_function(self, hash_value, step):
        start_idx = (step * 8) % 24
        hex_substring = hash_value[start_idx:start_idx + 8]

        try:
            hash_int = int(hex_substring, 16)
        except ValueError:
            hash_int = 0

        index = hash_int % len(self.passwords)
        return self.passwords[index]

Explanation:
It takes an 8-character substring of the hash (different each step).
Converts that substring from hexadecimal to an integer.
Uses the modulo operator to find a valid index within the password list.
Returns the password at that index as the next plaintext candidate.
This ensures each chain step generates a deterministic but varied mapping from hash → password.
