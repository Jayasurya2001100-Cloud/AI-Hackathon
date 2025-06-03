import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from preprocess import preprocess_data, save_class_names
import os
import datetime

def create_model(num_classes):
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False  # Freeze feature extractor

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)  # Reduces overfitting
    x = Dense(128, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    return model

def train():
    print("🔍 Preprocessing dataset...")
    train_gen, val_gen = preprocess_data('../dataset')
    num_classes = train_gen.num_classes

    model = create_model(num_classes)

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # 📦 Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-6, verbose=1)
    checkpoint_cb = ModelCheckpoint('../backend/best_model.h5', save_best_only=True, monitor='val_loss', verbose=1)

    # (Optional) TensorBoard
    log_dir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    tensorboard_cb = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    print("🚀 Starting training on CPU...")
    model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=10,
    callbacks=[early_stopping, reduce_lr, checkpoint_cb, tensorboard_cb]
)


    model.save('../backend/model.h5')
    save_class_names(train_gen.class_indices, '../backend/class_names.txt')
    print("✅ Training complete. Model and class names saved.")

if __name__ == "__main__":
    print("🧠 TensorFlow devices available:", tf.config.list_physical_devices())
    train()
