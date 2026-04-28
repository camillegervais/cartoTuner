import numpy as np

def get_lap_extremes(sLap_ref):
    """
    Determine the start and end indices of the lap in the reference trajectory, by looking at the sLap values. The lap should start at the first point where sLap is close to 0, and end at the first point where sLap decreases by more than 100 (which would indicate a new lap). This is necessary to make sure we are on one and only one lap of the track, and to remove the points at the beginning and at the end of the trajectory where the sLap is not consistent.

    Input: - sLap: array of sLap values for the reference trajectory
           - s_track: array of s values along the track, used to determine if the first point of the reference trajectory is at the beginning of the track or not
           - sample_length: length of the reference trajectory

    Output: - valid_indices: boolean array of the same length as sLap, with True for the points that are on the first lap and False for the points that are not
            - start_idx: index of the first point of the lap
            - end_idx: index of the last point of the lap
    """
    start_idx = 1
    if sLap_ref[0] > np.max(sLap_ref) * 0.5:
        potential_starts = np.where(sLap_ref < 50)[0]
        if len(potential_starts) > 0:
            start_idx = potential_starts[0]

    end_idx = len(sLap_ref)
    if np.any(np.diff(sLap_ref[start_idx:]) < -100):
        end_idx = np.where(np.diff(sLap_ref[start_idx:]) < -100)[0][0]  # Find the first index where sLap decreases by more than 100, which would indicate a new lap
    
    # Create a mask to keep only the points between the start and the end of the lap
    valid_indices = np.ones_like(sLap_ref, dtype=bool)
    valid_indices[:start_idx] = False
    valid_indices[end_idx:] = False
    return valid_indices, start_idx, end_idx

def clean_input_data(mat_data):
    """
    Apply all the post processing defined in this file to the input data for telemetry
    """
    input_signals = [key for key in mat_data.keys() if key not in ['__header__', '__version__', '__globals__']]
    mat_data = {
        signal: np.array(mat_data[signal].flatten().reshape(-1).T) for signal in input_signals
    }
    valid_indices, start_idx, end_idx = get_lap_extremes(mat_data['sLap'])
    for key in mat_data.keys():
        mat_data[key] = mat_data[key][valid_indices]
    return mat_data