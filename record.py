import classify
import numpy as np


CHUNK = 1000
RATE = 16000
RECORD_SECONDS = 2
WINDOW_STEP = RATE // 4

THRESHOLD = .1  # The threshold intensity that defines silence


FRAME_COUNT = RATE // CHUNK * RECORD_SECONDS

CENTER_INDEX = FRAME_COUNT // 2


def get_mass_center_idx(weights):
    indexes = np.array(range(1, len(weights)+1))
    sum_of_weights = 0
    weighted_sum = 0
    for i in indexes:
        current = weights[i-1]
        sum_of_weights += current
        weighted_sum += (current * i)
    return weighted_sum // sum_of_weights, sum_of_weights


def get_sound_data(mic_data):
    frames = []
    frame_square_sums = []
    for frame in mic_data:
        frames.append(frame)
        square_sum = sum(frame**2)
        frame_square_sums.append(square_sum)

        while len(frames) > FRAME_COUNT:
            frames.pop(0)
            frame_square_sums.pop(0)

        if len(frames) < FRAME_COUNT:
            continue

        mass_center_idx, total_weight = get_mass_center_idx(frame_square_sums)
        if total_weight < THRESHOLD:
            continue

        if mass_center_idx == CENTER_INDEX:
            all_frames = np.concatenate(frames)
            sound_data = np.reshape(all_frames, (len(all_frames), 1))
            yield sound_data


def get_labels(sound_data):
    classify.load_graph()
    labels = classify.load_labels()

    for sound_data in sound_data:
        relevant_predictions = []
        for start_idx in range(0, len(sound_data)-RATE, WINDOW_STEP):
            window = sound_data[start_idx:RATE+start_idx]
            result = classify.run_graph(window, RATE)
            relevant_predictions.append(result)
            #idx, score, label = classify.get_best(result, labels)
            #print(label, score)
        aggregated_result = np.sum(np.array(relevant_predictions)**2, axis=0)
        idx, score, label = classify.get_best(aggregated_result, labels)
        yield label