"""
DNA helix animation for the GenoPhenoPath application.

This module provides a text-based DNA helix animation used during loading
and transitional states in the application.

Functions in this module are used in:
- frontend.frontB.app.main: For loading animation
- frontend.frontB.display.chart: For transition animations
"""

import math
import time
import streamlit as st
from typing import List, Tuple, Any

def render_dna_frame(frame_num: int, width: int = 70, height: int = 50) -> str:
    """
    Generate a single frame of DNA helix animation.
    
    Args:
        frame_num: Animation frame number
        width: Width of the animation frame
        height: Height of the animation frame
        
    Returns:
        String representing a single animation frame
        
    Used in:
    - frontend.frontB.app.main.load_data_with_animation
    - frontend.frontB.display.chart.show_transition_animation
    """
    # Configuration
    radius = 15
    helix_length = 25
    dna_chars = ['G', 'T', 'C', 'A']  # DNA nucleotide characters
    
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
        phase = y_offset / 4 + frame_num / 10
        
        # Determine which character to use based on position
        char_index = (y_offset + helix_length) % 4
        current_char = dna_chars[char_index]
        
        # Calculate x positions for the two strands (opposite sides of the helix)
        x1 = center_x + int(radius * math.sin(phase))
        x2 = center_x + int(radius * math.sin(phase + math.pi))
        
        # Place characters if in bounds
        if 0 <= x1 < width:
            screen[y][x1] = current_char
        if 0 <= x2 < width:
            # Use complementary base pair on opposite strand
            complementary_index = (char_index + 2) % 4
            screen[y][x2] = dna_chars[complementary_index]
            
        # Add connecting rungs between the strands (less frequently)
        if y % 4 == 0:
            # Calculate the beginning and end of the rung
            if x1 > x2:
                x1, x2 = x2, x1
            
            # Draw the rung
            for x in range(x1 + 1, x2):
                if 0 <= x < width:
                    # Use hyphen for the connecting rungs
                    screen[y][x] = '-'
    
    # Convert the 2D screen array to a string
    return '\n'.join(''.join(row) for row in screen)

def generate_animation_frames(num_frames: int = 100, width: int = 70, height: int = 50) -> List[str]:
    """
    Generate all frames for the DNA animation.
    
    Args:
        num_frames: Number of animation frames to generate
        width: Width of the animation frame
        height: Height of the animation frame
        
    Returns:
        List of animation frame strings
        
    Used in:
    - frontend.frontB.app.main.load_data_with_animation
    """
    return [render_dna_frame(i, width, height) for i in range(num_frames)]

def display_dna_animation(
    placeholder: Any,
    frames: List[str], 
    frame_index: int,
    duration: float = 0.15
) -> int:
    """
    Display a single frame of the DNA animation and advance to the next frame.
    
    Args:
        placeholder: Streamlit container to display the animation
        frames: List of animation frame strings
        frame_index: Current frame index
        duration: Duration to display the frame (in seconds)
        
    Returns:
        Next frame index
        
    Used in:
    - frontend.frontB.app.main.load_data_with_animation
    - frontend.frontB.display.chart.show_transition_animation
    """
    # Display the current frame
    placeholder.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: rgba(0, 0, 0, 0.8); border-radius: 10px;">
        <div style="font-family: monospace; white-space: pre; color: #50fa7b; text-shadow: 0 0 5px rgba(80, 250, 123, 0.7);">
        {frames[frame_index]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add delay to control animation speed
    time.sleep(duration)
    
    # Return the next frame index
    return (frame_index + 1) % len(frames)