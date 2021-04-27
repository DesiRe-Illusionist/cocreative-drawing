import numpy as np
import pathlib

from ml_agent.sketch_rnn.sketch_rnn_train import *
from ml_agent.sketch_rnn.model import *
from ml_agent.sketch_rnn.utils import *
from ml_agent.sketch_rnn.rnn import *

import random

models_root_dir = pathlib.Path(__file__).parent / "models/"
model_dir = pathlib.Path(__file__).parent / "models/images"

model_params, eval_model_params, sample_model_params = load_model(model_dir)
tf.compat.v1.disable_eager_execution()
reset_graph()
model = Model(model_params)
eval_model = Model(eval_model_params, reuse=True)
sample_model = Model(sample_model_params, reuse=True)

sess = tf.compat.v1.InteractiveSession()
sess.run(tf.compat.v1.global_variables_initializer())

load_checkpoint(sess, model_dir)


def predict_next_stroke(coords, blind=True, seq_len=100):
    out = coords_to_stroke3(coords)
    z, stks = encode(out)
    temp = random.random()
    print(f"Temperature : {temp}")
    final_strokes, everything = decode(
        z, temperature=temp, seq_len=seq_len, factor=0.2, blind=blind, stks=stks, out=out
    )
    print("Drawing")
    return strokes_to_lines(final_strokes, blind)


def coords_to_stroke3(coords):
    out = []
    for line in coords:
        for i, point in enumerate(line):
            p = [float(x) / 12 for x in point]
            if i == (len(line) - 1):
                p.append(1.0)
            else:
                p.append(0.0)
            out.append(p)
    out = np.array(out)
    out[1:, 0:2] -= out[:-1, 0:2]
    return out


def encode(input_strokes):
    strokes = to_big_strokes(input_strokes, max_len=eval_model.hps.max_seq_len).tolist()
    strokes.insert(0, [0, 0, 1, 0, 0])
    seq_len = [len(input_strokes)]
    return (
        sess.run(
            eval_model.batch_z,
            feed_dict={
                eval_model.input_data: [strokes],
                eval_model.sequence_lengths: seq_len,
            },
        )[0],
        strokes,
    )


def pad_batch(model, batch, max_len):
    """Pad the batch to be stroke-5 bigger format as described in paper."""
    start_stroke_token = [0, 0, 1, 0, 0]
    result = np.zeros((model.hps.batch_size, max_len + 1, 5), dtype=float)
    assert len(batch) == model.hps.batch_size
    for i in range(model.hps.batch_size):
        l = len(batch[i])
        assert l <= max_len
        result[i, 0:l, 0:2] = batch[i][:, 0:2]
        result[i, 0:l, 3] = batch[i][:, 2]
        result[i, 0:l, 2] = 1 - result[i, 0:l, 3]
        result[i, l:, 4] = 1
        # put in the first token, as described in sketch-rnn methodology
        result[i, 1:, :] = result[i, :-1, :]
        result[i, 0, :] = 0
        result[i, 0, 2] = start_stroke_token[2]  # setting S_0 from paper.
        result[i, 0, 3] = start_stroke_token[3]
        result[i, 0, 4] = start_stroke_token[4]
    return result


def sample(
    sess,
    model,
    seq_len=250,
    temperature=1.0,
    greedy_mode=False,
    z=None,
    stks=None,
    blind=True,
):
    """Samples a sequence from a pre-trained model."""

    def adjust_temp(pi_pdf, temp):
        pi_pdf = np.log(pi_pdf) / temp
        pi_pdf -= pi_pdf.max()
        pi_pdf = np.exp(pi_pdf)
        pi_pdf /= pi_pdf.sum()
        return pi_pdf

    def get_pi_idx(x, pdf, temp=1.0, greedy=False):
        """Samples from a pdf, optionally greedily."""
        if greedy:
            return np.argmax(pdf)
        pdf = adjust_temp(np.copy(pdf), temp)
        accumulate = 0
        for i in range(0, pdf.size):
            accumulate += pdf[i]
            if accumulate >= x:
                return i
        tf.logging.info("Error with sampling ensemble.")
        return -1

    def sample_gaussian_2d(mu1, mu2, s1, s2, rho, temp=1.0, greedy=False):
        if greedy:
            return mu1, mu2
        mean = [mu1, mu2]
        s1 *= temp * temp
        s2 *= temp * temp
        cov = [[s1 * s1, rho * s1 * s2], [rho * s1 * s2, s2 * s2]]
        x = np.random.multivariate_normal(mean, cov, 1)
        return x[0][0], x[0][1]

    prev_x = np.zeros((1, 1, 5), dtype=np.float32)
    prev_x[0, 0, 2] = 1  # initially, we want to see beginning of new stroke

    if z is None:
        z = np.random.randn(1, model.hps.z_size)  # not used if unconditional

    if not model.hps.conditional:
        prev_state = sess.run(model.initial_state)
    else:
        prev_state = sess.run(model.initial_state, feed_dict={model.batch_z: z})

    len_stks = len(stks)
    strokes = np.zeros((seq_len, 5), dtype=np.float32)
    mixture_params = []

    greedy = greedy_mode
    temp = temperature

    if not blind:
        for j, stk in enumerate(stks):
            i = j + 1
            dta = pad_batch(sample_model, np.array([[stk]]), 1)
            if not model.hps.conditional:
                feed = {
                    model.input_x: prev_x,
                    model.sequence_lengths: [1],
                    model.initial_state: prev_state,
                    model.input_data: dta,
                }
            else:
                feed = {
                    model.input_x: prev_x,
                    model.sequence_lengths: [1],
                    model.initial_state: prev_state,
                    model.batch_z: z,
                    model.input_data: dta,
                }

            params = sess.run(
                [
                    model.pi,
                    model.mu1,
                    model.mu2,
                    model.sigma1,
                    model.sigma2,
                    model.corr,
                    model.pen,
                    model.final_state,
                ],
                feed,
            )

            [o_pi, o_mu1, o_mu2, o_sigma1, o_sigma2, o_corr, o_pen, next_state] = params

            idx = get_pi_idx(random.random(), o_pi[0], temp, greedy)

            idx_eos = get_pi_idx(random.random(), o_pen[0], temp, greedy)
            eos = [0, 0, 0]
            eos[idx_eos] = 1

            next_x1, next_x2 = sample_gaussian_2d(
                o_mu1[0][idx],
                o_mu2[0][idx],
                o_sigma1[0][idx],
                o_sigma2[0][idx],
                o_corr[0][idx],
                np.sqrt(temp),
                greedy,
            )

            params = [
                o_pi[0],
                o_mu1[0],
                o_mu2[0],
                o_sigma1[0],
                o_sigma2[0],
                o_corr[0],
                o_pen[0],
            ]

            mixture_params.append(params)

            prev_x = np.zeros((1, 1, 5), dtype=np.float32)
            prev_x[0][0] = np.array(
                [next_x1, next_x2, eos[0], eos[1], eos[2]], dtype=np.float32
            )
            prev_state = next_state

        strokes = np.zeros((seq_len, 5), dtype=np.float32)
        mixture_params = []

    for i in range(seq_len):
        if not model.hps.conditional:
            feed = {
                model.input_x: prev_x,
                model.sequence_lengths: [1],
                model.initial_state: prev_state,
            }
        else:
            feed = {
                model.input_x: prev_x,
                model.sequence_lengths: [1],
                model.initial_state: prev_state,
                model.batch_z: z,
            }

        params = sess.run(
            [
                model.pi,
                model.mu1,
                model.mu2,
                model.sigma1,
                model.sigma2,
                model.corr,
                model.pen,
                model.final_state,
            ],
            feed,
        )

        [o_pi, o_mu1, o_mu2, o_sigma1, o_sigma2, o_corr, o_pen, next_state] = params

        idx = get_pi_idx(random.random(), o_pi[0], temp, greedy)

        idx_eos = get_pi_idx(random.random(), o_pen[0], temp, greedy)
        eos = [0, 0, 0]
        eos[idx_eos] = 1

        next_x1, next_x2 = sample_gaussian_2d(
            o_mu1[0][idx],
            o_mu2[0][idx],
            o_sigma1[0][idx],
            o_sigma2[0][idx],
            o_corr[0][idx],
            np.sqrt(temp),
            greedy,
        )

        strokes[i, :] = [next_x1, next_x2, eos[0], eos[1], eos[2]]

        params = [
            o_pi[0],
            o_mu1[0],
            o_mu2[0],
            o_sigma1[0],
            o_sigma2[0],
            o_corr[0],
            o_pen[0],
        ]

        mixture_params.append(params)

        prev_x = np.zeros((1, 1, 5), dtype=np.float32)
        prev_x[0][0] = np.array(
            [next_x1, next_x2, eos[0], eos[1], eos[2]], dtype=np.float32
        )
        prev_state = next_state
    return strokes, mixture_params


def decode(
    z_input=None,
    draw_mode=True,
    temperature=0.1,
    factor=0.3,
    seq_len=eval_model.hps.max_seq_len,
    blind=True,
    stks=None,
    out=None,
):
    z = None
    if z_input is not None:
        z = [z_input]
    sample_strokes, m = sample(
        sess,
        sample_model,
        seq_len=seq_len,
        temperature=temperature,
        z=z,
        stks=stks,
        blind=blind,
    )

    strokes = to_normal_strokes(sample_strokes)
    strokes[-1][2] = 1
    enc_strokes = to_normal_strokes(np.array(stks))

    everything = np.concatenate((strokes, out), 0)
    return strokes, everything


def strokes_to_lines(strokes, blind):
    """Convert stroke-3 format to polyline format."""
    x = 0
    y = 0
    lines = []
    line = []
    for i in range(len(strokes)):
        if strokes[i, 2] == 1:
            x += float(strokes[i, 0])
            y += float(strokes[i, 1])
            line.append([x, y])
            lines.append(line)
            line = []
        else:
            x += float(strokes[i, 0])
            y += float(strokes[i, 1])
            line.append([x, y])
    if len(line) > 0:
        lines.append(line)

    scale = 6
    min_val = 0
    final_lines = []
    for line in lines:

        line = np.array(line).astype(float)
        line = line * scale

        temp_min_val = float(np.amin(line))
        if temp_min_val < min_val:
            min_val = temp_min_val
        line = line.tolist()
        final_lines.append(line)
    scaled_final_lines = []
    for line in final_lines:
        line = np.array(line).astype(float)
        line -= min_val - 50
        line = line.tolist()
        scaled_final_lines.append(line)
    return scaled_final_lines
