import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

def preprocess_data(dataset_dir):
    # Data augmentation + normalization
    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2,
        horizontal_flip=True,
        rotation_range=20
    )
    
    train_generator = datagen.flow_from_directory(
        dataset_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    val_generator = datagen.flow_from_directory(
        dataset_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    return train_generator, val_generator

def save_class_names(class_indices, filepath):
    # Save class names sorted by class index order
    sorted_classes = sorted(class_indices.items(), key=lambda x: x[1])
    with open(filepath, 'w') as f:
        for cls, _ in sorted_classes:
            f.write(f"{cls}\n")
