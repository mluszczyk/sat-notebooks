from time import localtime

import tensorflow as tf

import numpy as np

LEARNING_RATE = 0.01


def model_fn(features, labels, mode):
    matrix_input = features["matrix"]

    summed = tf.reduce_sum(matrix_input, 2)
    summed = tf.reshape(summed, [-1, int(matrix_input.shape[1]), 1])

    layer = tf.layers.dense(summed, 1)

    output_layer = layer

    predictions = {
        "probabilities": output_layer
    }
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    loss = tf.losses.mean_squared_error(labels=labels,
                                        predictions=output_layer)
    tf.summary.histogram('labels', labels)
    tf.summary.scalar('loss', loss)

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(
            learning_rate=LEARNING_RATE)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss,
                                          train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {"accuracy": tf.metrics.accuracy(
        labels=labels, predictions=predictions["probabilities"])}
    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def get_model_name():
    t = localtime()
    modelname = "sat{}_{}_{}_{}_{}".format(
        t.tm_year, str(t.tm_mon).zfill(2), str(t.tm_mday).zfill(2),
        str(t.tm_hour).zfill(2), str(t.tm_min).zfill(2))
    return modelname


sat_input = np.array(
    [[[0., 0., 1.],
      [0., 1., 0.],
      [0., 0., 1.],
      [-1., 0., 0.]
      ]])

sat_output = np.array(
    [[[2.],
      [1.],
      [0.],
      [-1.],
      ]])


v_sat_input = np.array(
    [[[0., 0., 1.],
      [0., 1., 0.]
      ]])

v_sat_output = np.array(
    [[[2.],
      [1.]
      ]])

def main():
    classifier = tf.estimator.Estimator(
        model_fn=model_fn, model_dir="./sat1_models/{}".format(get_model_name()))

    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"matrix": sat_input},
        y=np.array(sat_output),
        batch_size=1,
        num_epochs=1,
        shuffle=True)

    valid_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"matrix": v_sat_input},
        y=np.array(v_sat_output),
        batch_size=1,
        num_epochs=1,
        shuffle=True)

    for epoch in range(10):
        classifier.train(
            input_fn=train_input_fn, steps=None)
        res = classifier.evaluate(
            input_fn=valid_input_fn, steps=None)
        print(res)


if __name__ == "__main__":
    main()
