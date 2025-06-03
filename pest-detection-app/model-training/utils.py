import matplotlib.pyplot as plt
import json

def plot_history(history):
    plt.plot(history.history['accuracy'], label='Train Acc')
    plt.plot(history.history['val_accuracy'], label='Val Acc')
    plt.title('Training History')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

def save_labels(class_indices, path="class_labels.txt"):
    labels = [label for label, _ in sorted(class_indices.items(), key=lambda x: x[1])]
    with open(path, 'w') as f:
        for label in labels:
            f.write(f"{label}\n")
