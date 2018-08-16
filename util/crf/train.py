import os
from os import makedirs
from os.path import dirname
from languageflow.model.crf import CRF

from util.crf.conlleval import evaluate, parse_args
from util.crf.pos_tag.features import template
from util.crf.pos_tag.model import CRFModel
from .load_data import load_dataset
from .transformer.custom_transformer import CustomTransformer


def train(train_path, model_path):
    train_set = []

    train_set += load_dataset(train_path)
    print("Load data from file", train_path)
    transformer = CustomTransformer(template)
    X, y = transformer.transform(train_set)

    # train
    params = {
        'c1': 1.0,  # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 1000,  #
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    }
    folder = dirname(model_path)
    try:
        makedirs(folder)
    except:
        pass
    estimator = CRF(params=params, filename=model_path)
    estimator.fit(X, y)


def _remove_file(output_path):
    try:
        os.remove(output_path)
    except:
        pass


def train_test(train_path, test_path):
    model_path = "model.tmp.bin"
    output_path = "output.txt"
    _remove_file(output_path)
    output = open(output_path, "a")
    train(train_path, model_path)
    estimator = CRFModel.instance(model_path)

    test = load_dataset(test_path)
    for sample in test:
        sentence = [token[0] for token in sample]
        y_test = [token[1] for token in sample]
        y_pred = estimator.predict(sentence)
        for i in range(len(y_test)):
            line = "{}\t{}\t{}\n".format(y_pred[i][0], y_test[i], y_pred[i][1])
            output.write(line)
        output.write("\n")

    class Args(object):
        pass

    args = Args()
    args.latex = False
    args.raw = False
    args.delimiter = None
    args.oTag = "O"
    evaluate(open(output_path), args)
