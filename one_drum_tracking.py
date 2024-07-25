import pandas as pd
import numpy as np
import time
import pygame
import os
import threading
from scipy.signal import find_peaks, detrend
import matplotlib.pyplot as plt

# Detect peaks
def detect_peaks(df, column_name='acc_z', height=5, distance=None):
    peaks, _ = find_peaks(df[column_name].dropna(), height=height, distance=distance)
    return peaks

# Calculate positions and velocity
def calculate_positions_and_velocity(df, delta_t=0.01):
    df = df.copy()
    if len(df) < 2:
        return df  # Return empty DataFrame if there are not enough rows for calculation

    df['v_x'] = 0.0
    df['v_y'] = 0.0
    df['v_z'] = 0.0
    df['x_pos'] = 0.0
    df['y_pos'] = 0.0
    df['z_pos'] = 0.0
    df['acc_x'] = detrend(df['acc_x'])
    df['acc_y'] = detrend(df['acc_y'])
    df['acc_z'] = detrend(df['acc_z'])
    
    for i in range(2, len(df)):
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

# Drum boundaries and other constants
drum_boundaries = {
    'hihats': {'x_min': -0.5, 'y_min': -0.5, 'x_max': 0, 'y_max': 0},
    'crash': {'x_min': -0.5, 'y_min': 0, 'x_max': 0, 'y_max': 0.5},
    'hitoms': {'x_min': 0, 'y_min': 0, 'x_max': 0.5, 'y_max': 0.5},
    'lotoms': {'x_min': 0, 'y_min': -0.5, 'x_max': 0.5, 'y_max': 0},
    'ride': {'x_min': 0.5, 'y_min': -10, 'x_max': 10, 'y_max': 10},
    'snare': {'x_min': -10, 'y_min': -10, 'x_max': -0.5, 'y_max': 10}
}

z_threshold = -5

def find_drum_type(df, peak):
    detected_drum = None

    x_pos = df.loc[peak, 'x_pos']
    y_pos = df.loc[peak, 'y_pos']
    z_pos = df.loc[peak, 'z_pos']
        
    if z_pos > z_threshold:
        for drum, bounds in drum_boundaries.items():
            if (bounds['x_min'] <= x_pos <= bounds['x_max'] and 
                bounds['y_min'] <= y_pos <= bounds['y_max']):
                detected_drum = drum
                return detected_drum
            
    return detected_drum

def play_drum_sound(drum_type, sound_level):
    base_path = "samples\\%s" % (drum_type)
    file_name = f"{drum_type}{sound_level}.wav"
    file_path = os.path.join(base_path, file_name)
    print(file_path)
    if os.path.exists(file_path):
        pygame.mixer.init()
        sound = pygame.mixer.Sound(file_path)
        sound.play()
    else:
        print("File not found")

def play_sound_thread(drum_type, sound_level):
    sound_thread = threading.Thread(target=play_drum_sound, args=(drum_type, sound_level))
    sound_thread.start()

def find_drum_sound_level(df, peak):
    lvl1 = 5
    lvl2 = 8
    lvl3 = 11
    lvl4 = 13.5
    lvl5 = 14
    lvl6 = 16.5
    lvl7 = 17
    lvl8 = 18.5
    lvl9 = 20
    
    acceleration_Value = df.loc[peak, 'acc_z']
    print(acceleration_Value)
    
    if lvl1 <= acceleration_Value < lvl2:
        return 0
    if lvl2 <= acceleration_Value < lvl3:
        return 1
    if lvl3 <= acceleration_Value < lvl4:
        return 2
    if lvl4 <= acceleration_Value < lvl5:
        return 3
    if lvl5 <= acceleration_Value < lvl6:
        return 4
    if lvl6 <= acceleration_Value < lvl7:
        return 5
    if lvl7 <= acceleration_Value < lvl8:
        return 6
    if lvl8 <= acceleration_Value < lvl9:
        return 7

def give_drumtype_and_level(df, peaks):
    pygame.init()
    pygame.mixer.init()
    for peak in peaks:
        drum_type = find_drum_type(df, peak)
        sound_level = find_drum_sound_level(df, peak)
        print(peak, drum_type, sound_level)
        play_sound_thread(drum_type, sound_level)
        

def read_and_process_csv(csv_file, interval=1):
    last_index = 0
        
    while True:
        df = pd.read_csv(csv_file)
        if len(df) > last_index:
            new_data = df.iloc[last_index:].reset_index(drop=True)  # Reset the index here
            last_index = len(df)

            # Calculate positions and velocity
            df_positions = calculate_positions_and_velocity(new_data)

            # Detect peaks
            peaks = detect_peaks(df_positions)
            print("Detected peaks at:", peaks)

            # Process drum hits
            give_drumtype_and_level(df_positions, peaks)

          

          

        time.sleep(interval)


csv_file = 'drum1.csv'
read_and_process_csv(csv_file)
