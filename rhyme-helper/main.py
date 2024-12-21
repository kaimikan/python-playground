import pronouncing

def generate_rhyming_scheme(word, num_rhymes=10):
    """
    Generate a rhyming scheme based on a given word.
    
    Parameters:
        word (str): The base word for generating rhymes.
        num_rhymes (int): The number of rhyming words to include in the scheme.
    
    Returns:
        str: A rhyming scheme based on the input word.
    """
    rhymes = pronouncing.rhymes(word)
    if not rhymes:
        return f"No rhymes found for the word '{word}'."
    
    # Limit the number of rhymes if specified
    rhymes = rhymes[:num_rhymes]
    
    # Create a rhyming scheme
    scheme = ""
    for i, rhyme in enumerate(rhymes, start=1):
        scheme += f"{i}: {rhyme}\n"
    
    return scheme

# Main program loop
if __name__ == "__main__":
    print("Rhyming Scheme Generator")
    print("Type 'exit' or 'quit' to stop the program.")
    print("Type 'set num_rhymes [number]' to adjust the number of rhymes displayed.\n")
    
    num_rhymes = 10  # Default number of rhymes
    
    while True:
        user_input = input("Enter a word or command: ").strip().lower()
        
        # Handle exit command
        if user_input in {"exit", "quit"}:
            print("Goodbye!")
            break
        
        # Handle setting num_rhymes
        if user_input.startswith("set num_rhymes"):
            try:
                _, _, new_value = user_input.split()
                num_rhymes = int(new_value)
                if num_rhymes < 1:
                    print("Please enter a positive number for num_rhymes.\n")
                else:
                    print(f"Number of rhymes set to {num_rhymes}.\n")
            except (ValueError, IndexError):
                print("Invalid command. Usage: set num_rhymes [number]\n")
            continue
        
        # Generate and display rhyming scheme
        print("\nRhyming Scheme:")
        print(generate_rhyming_scheme(user_input, num_rhymes))
        print()
