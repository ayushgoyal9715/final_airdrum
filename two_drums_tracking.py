import pandas as pd
import numpy as np
import math
import time
import pygame
import os
import threading
from scipy.signal import find_peaks, detrend

# Net acceleration calculation
def net_acceleration(df):
    df['net_acc'] = np.sqrt(df['acc_x']**2 + df['acc_y']**2 + df['acc_z']**2)
    return df

# Peak detection with dynamic threshold
def detect_peaks(df, column_name='net_acc', height=6, distance=None):
    peaks, _ = find_peaks(df[column_name].dropna(), height=height, distance=distance)
    return peaks

# Calculate positions and velocity with reset interval
def calculate_positions_and_velocity(df, delta_t=0.01, reset_interval=20, displacement_reset_interval=20):
    df = df.copy()
    df['v_x'] = 0.0
    df['v_y'] = 0.0
    df['v_z'] = 0.0
    df['x_pos'] = 0.0
    df['y_pos'] = 0.0
    df['z_pos'] = 0.0
    df['acc_x'] = detrend(df['acc_x'])
    df['acc_y'] = detrend(df['acc_y'])
    df['acc_z'] = detrend(df['acc_z'])
    
    for i in range(1, len(df)):
        if i % reset_interval == 0:
            df.loc[i, 'v_x'] = 0.0
            df.loc[i, 'v_y'] = 0.0
            df.loc[i, 'v_z'] = 0.0
        
        if i % displacement_reset_interval == 0:
            df.loc[i, 'x_pos'] = 0.0
            df.loc[i, 'y_pos'] = 0.0
            df.loc[i, 'z_pos'] = 0.0
        else:
            acc_x = df.loc[i, 'acc_x']
            acc_y = df.loc[i, 'acc_y']
            acc_z = df.loc[i, 'acc_z']
            
            df.loc[i, 'v_x'] = df.loc[i-1, 'v_x'] + acc_x * delta_t
            df.loc[i, 'v_y'] = df.loc[i-1, 'v_y'] + acc_y * delta_t
            df.loc[i, 'v_z'] = df.loc[i-1, 'v_z'] + acc_z * delta_t
            
            df.loc[i, 'x_pos'] = df.loc[i-1, 'x_pos'] + df.loc[i-1, 'v_x'] * delta_t + 0.5 * acc_x * (delta_t ** 2)
            df.loc[i, 'y_pos'] = df.loc[i-1, 'y_pos'] + df.loc[i-1, 'v_y'] * delta_t + 0.5 * acc_y * (delta_t ** 2)
            df.loc[i, 'z_pos'] = df.loc[i-1, 'z_pos'] + df.loc[i-1, 'v_z'] * delta_t + 0.5 * acc_z * (delta_t ** 2)
    
    df['v_net'] = np.sqrt(df['v_x']**2 + df['v_y']**2 + df['v_z']**2)
    df['x_net'] = np.sqrt(df['x_pos']**2 + df['y_pos']**2 + df['z_pos']**2) 
    
    return df

# Define drum boundaries and other constants
drum_boundaries = {
    'hitoms': {'x_min': -4.5, 'y_min': 0, 'x_max': -1.5, 'y_max': 1},
    'hihats': {'x_min': -1.5, 'y_min': 0, 'x_max': 1.5, 'y_max': 1},
    'lotoms': {'x_min': 1.5, 'y_min': 0, 'x_max': 4.5, 'y_max': 1},
    'ride': {'x_min': -4.5, 'y_min': -1, 'x_max': -1.5, 'y_max': 0},
    'snare': {'x_min': -1.5, 'y_min': -1, 'x_max': 1.5, 'y_max': 0},
    'crash': {'x_min': 1.5, 'y_min': -1, 'x_max': 4.5, 'y_max': 0}
}
z_threshold = -5

# Find the drum type
def find_drum_type(df, peak):
    detected_drum = None
    x_pos = df.loc[peak, 'x_pos']
    y_pos = df.loc[peak, 'y_pos']
    z_pos = df.loc[peak, 'z_pos']
        
    if z_pos > z_threshold:
        for drum, bounds in drum_boundaries.items():
            if bounds['x_min'] <= x_pos <= bounds['x_max'] and bounds['y_min'] <= y_pos <= bounds['y_max']:
                detected_drum = drum
                return detected_drum
    return detected_drum

# Play drum sound
def play_drum_sound(drum_type, sound_level):
    base_path = f"samples/{drum_type}"
    file_name = f"{drum_type}{sound_level}.wav"
    file_path = os.path.join(base_path, file_name)
    print(file_path)
    if os.path.exists(file_path):
        pygame.mixer.init()
        sound = pygame.mixer.Sound(file_path)
        sound.play()
    else:
        print("File not found")

# Multithreading for playing sound
def play_sound_thread(drum_type, sound_level):
    sound_thread = threading.Thread(target=play_drum_sound, args=(drum_type, sound_level))
    sound_thread.start()

# Find drum sound level
def find_drum_sound_level(df, peak):
    levels = [6, 8, 12, 16, 20, 24, 28, 32, 36]
    
    acceleration_value = abs(df.loc[peak, 'acc_z'])
    print(acceleration_value)
    
    for i, lvl in enumerate(levels):
        if acceleration_value < lvl:
            return i
    return len(levels)

# Process drum hits
def give_drumtype_and_level(df, peaks):
    pygame.init()
    pygame.mixer.init()
    for peak in peaks:
        drum_type = find_drum_type(df, peak)
        sound_level = find_drum_sound_level(df, peak)
        print(peak, drum_type, sound_level)
        if drum_type:
            play_sound_thread(drum_type, sound_level)
        time.sleep(0.1)  # Reduced sleep time for faster processing

# Read and process CSV in real-time
def read_and_process_csv(csv_file, interval=1, buffer_size=100, reset_interval=10, displacement_reset_interval=150):
    buffer = pd.DataFrame()
    total_rows_processed = 0
    last_position = 0
    
    while True:
        df = pd.read_csv(csv_file)
        new_data = df.iloc[last_position:]
        last_position = len(df)
        
        if not new_data.empty:
            if buffer.empty:
                buffer = new_data
            else:
                buffer = pd.concat([buffer, new_data]).reset_index(drop=True)
                if len(buffer) > buffer_size:
                    buffer = buffer.iloc[-buffer_size:].reset_index(drop=True)
            
            buffer = net_acceleration(buffer)
            buffer_positions = calculate_positions_and_velocity(buffer, reset_interval=20, displacement_reset_interval=20)
            peaks = detect_peaks(buffer_positions)
            total_rows_processed += len(new_data)
            print("Detected peaks at:", peaks)
            print("Total rows processed:", total_rows_processed)
            give_drumtype_and_level(buffer_positions, peaks)
        
        time.sleep(interval)

# Main function to start reading and processing
csv_file1 = 'drum1.csv'
csv_file2 = 'drum2.csv'

# Read and process both drum files
thread1 = threading.Thread(target=read_and_process_csv, args=(csv_file1,))
thread2 = threading.Thread(target=read_and_process_csv, args=(csv_file2,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
