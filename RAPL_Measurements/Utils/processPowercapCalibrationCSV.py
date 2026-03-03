import pandas as pd
import sys
import re

def process_csv(filename):
    # Read the CSV file
    data = pd.read_csv(filename, skip_blank_lines=True)

    # Clean up column names
    data.columns = [c.strip() for c in data.columns]

    # Drop rows that are repeated header lines (e.g., rows where Language == 'Language')
    if 'Language' in data.columns:
        data = data[data['Language'].astype(str).str.strip().str.lower() != 'language']

    # Ensure 'Package' column is numeric: extract first float from strings and coerce
    if 'Package' in data.columns:
        # Convert to string, extract first numeric token (handles space-separated lists), then to float
        data['Package'] = data['Package'].astype(str).str.extract(r'([-+]?\d*\.\d+|\d+)', expand=False)
        data['Package'] = pd.to_numeric(data['Package'], errors='coerce')

    # Drop rows where Package could not be converted
    data = data.dropna(subset=['Package'])

    # Ensure Powercap is numeric for proper sorting/grouping
    if 'Powercap' in data.columns:
        data['Powercap'] = pd.to_numeric(data['Powercap'].astype(str).str.strip(), errors='coerce')
        data = data.dropna(subset=['Powercap'])

    # Create a dictionary to store average results
    results = {}

    # Group the data by 'Powercap'
    grouped = data.groupby('Powercap')

    print(f"\n{'=' * 50}")
    print(f"{' Powercap Average Package Report ':^50}")
    print(f"{'=' * 50}\n")

    for powercap, group in grouped:
        if len(group) <= 2:
            # If there are 2 or fewer entries, averaging is not possible
            print(f"Powercap: {powercap}, not enough entries to calculate the average.")
            continue
        
        # Remove the entries with the maximum and minimum values in the 'Package' column
        max_package = group['Package'].max()
        min_package = group['Package'].min()
        
        # Filter the group, removing max and min
        filtered_group = group[(group['Package'] != max_package) & (group['Package'] != min_package)]

        # Calculate the average of the 'Package' column for the remaining values
        average_package = filtered_group['Package'].mean()
        
        # Store the result
        results[powercap] = average_package

    # Display the results and find the Powercap with the lowest average package
    lowest_average_powercap = None
    lowest_average_value = float('inf')

    print(f"{'Powercap':<15}{'Average Package':<20}")
    print(f"{'-' * 35}")
    
    # Print results sorted by Powercap
    for powercap in sorted(results.keys()):
        average = results[powercap]
        print(f"{powercap:<15}{average:<20.6f}")

        # Check if this is the lowest average package value
        if average < lowest_average_value:
            lowest_average_value = average
            lowest_average_powercap = powercap

    # Display the Powercap with the lowest average package
    print(f"\n{'=' * 35}")
    if lowest_average_powercap is not None:
        print(f"{'Powercap with the lowest average package:':<35} {lowest_average_powercap} (Average: {lowest_average_value:.6f})")
    else:
        print("No valid Powercaps to determine the lowest average.")

    print(f"{'=' * 35}")

def main():
    # Check if the filename was provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python process_csv.py <filename>")
        sys.exit(1)

    # Get the filename from the command-line arguments
    filename = sys.argv[1]

    # Process the provided CSV file
    process_csv(filename)

# Entry point of the program
if __name__ == "__main__":
    main()