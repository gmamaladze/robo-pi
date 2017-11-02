import numpy as np

RATE = 16000


def is_silence(data, threshold):
    square_mean = np.mean(data ** 2)
    return square_mean < threshold


def get_labels(data_stream, classifier, threshold):
    all_frames = np.array([], dtype=np.float)
    classifier.run(np.zeros((RATE, 1)))  # void call to avoid latency on firs word later
    print("Listening for commands:")
    for data in data_stream:
        all_frames = np.concatenate([all_frames, data])
        total_length = len(all_frames)
        if total_length < RATE:
            continue
        else:
            all_frames = all_frames[total_length - RATE:total_length]

        first_third = all_frames[0:RATE // 3]
        if is_silence(first_third, threshold):
            yield 0, 0, "."
            continue

        input_tensor = np.reshape(all_frames, (RATE, 1))
        yield classifier.run(input_tensor)


def get_confident_labels(labels_stream):
    confidence = 0
    last_idx = 0

    for idx, score, label in labels_stream:
        if confidence < 0:
            confidence += 1
            last_idx = 0
            continue

        if idx == 0 or idx != last_idx:
            last_idx = idx
            confidence = 0
            continue

        if idx == last_idx:
            if confidence > 2:
                yield label
                confidence = -3
                last_idx = 0
            else:
                confidence += 1


def calibrate_silence(data_stream, classifier, sample_count=10):
    max_silence = 0
    commands = np.array([0])
    frames = []
    print("Calibrating silence threshold. Please say random commands with 2-3 seconds pauses in between.")

    for data in data_stream:
        frames.append(data)
        all_frames = np.concatenate(frames)
        if len(all_frames) < RATE:
            continue
        sound_data = np.reshape(all_frames, (len(all_frames), 1))
        input_data = sound_data[0:RATE]
        idx, score, label = classifier.run(input_data)
        square_mean = np.mean(input_data ** 2)
        symbol = "." if idx == 0 else "*"
        print(symbol)
        frames = []
        if idx == 0:
            max_silence = max(max_silence, square_mean)
            sample_count -= 1
            if sample_count == 0:
                break
        else:
            if score > 0.5:
                np.append(commands, [square_mean])
    return max_silence, np.average(commands)
