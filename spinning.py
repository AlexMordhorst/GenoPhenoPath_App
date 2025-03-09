import math
import time
import os
import sys

# Configuration
width = 70
height = 30
frames = 60
speed = 0.05  # Lower is faster
radius = 10
helix_length = 25
density = 1.0  # Density of dots (1.0 = full density)
dna_chars = ['G', 'T', 'C', 'A']  # DNA nucleotide characters

def clear_screen():
    # Clear screen based on OS
    os.system('cls' if os.name == 'nt' else 'clear')

def render_dna(frame):
    # Create an empty screen buffer
    screen = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Calculate the center of the screen
    center_x = width // 2
    center_y = height // 2
    
    # Draw the two helical strands
    for y_offset in range(-helix_length, helix_length + 1):
        # Calculate the y position
        y = center_y + y_offset
        
        # Skip if out of bounds
        if y < 0 or y >= height:
            continue
        
        # Calculate the phase for this position
        phase = y_offset / 4 + frame / 10
        
        # Determine which character to use based on position
        char_index = (y_offset + helix_length) % 4
        current_char = dna_chars[char_index]
        
        # Calculate x positions for the two strands (opposite sides of the helix)
        x1 = center_x + int(radius * math.sin(phase))
        x2 = center_x + int(radius * math.sin(phase + math.pi))
        
        # Place characters if in bounds and meets density check
        if 0 <= x1 < width and random_check(density):
            screen[y][x1] = current_char
        if 0 <= x2 < width and random_check(density):
            # Use complementary base pair on opposite strand
            complementary_index = (char_index + 2) % 4
            screen[y][x2] = dna_chars[complementary_index]
            
        # Add connecting rungs between the strands (less frequently)
        if y % 4 == 0:
            # Calculate the beginning and end of the rung
            if x1 > x2:
                x1, x2 = x2, x1
            
            # Draw the rung
            for x in range(x1, x2 + 1):
                if 0 <= x < width and random_check(density * 0.7):
                    # Use hyphen for the connecting rungs
                    screen[y][x] = '-'
    
    # Convert the 2D screen array to a string
    return '\n'.join(''.join(row) for row in screen)

def random_check(probability):
    # Simple check to see if we should draw a point, based on density
    import random
    return random.random() < probability

def main():
    try:
        for frame in range(frames):
            clear_screen()
            dna = render_dna(frame)
            print(dna)
            
            # No signature at the bottom
            
            time.sleep(speed)
            
        # Loop the animation
        main()
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        print("\nAnimation stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
