import tensorflow as tf

def convert_model():
    model = tf.keras.models.load_model('../backend/model.h5')

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # Enable optimization for mobile
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()

    with open('../backend/model.tflite', 'wb') as f:
        f.write(tflite_model)

if __name__ == "__main__":
    convert_model()
