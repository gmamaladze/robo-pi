import os
import voicecmd
import classify

isRaspberryPi = (os.uname()[4][:3] == 'arm')
print("Is raspberry pi:", isRaspberryPi)

if isRaspberryPi:
    import mic_pi as mic
else:
    import mic


classifier = classify.Classifier()

max_silence, avg_sound = \
    voicecmd.calibrate_silence(
        mic.get_mic_data(),
        classifier)

threshold = (avg_sound - max_silence) / 4 + max_silence
print ("Threshold: ", threshold)
labels_stream = \
    voicecmd.get_confident_labels(
        voicecmd.get_labels(
            mic.get_mic_data(),
            classifier,
            threshold))


for current_label in labels_stream:
    print(current_label)

