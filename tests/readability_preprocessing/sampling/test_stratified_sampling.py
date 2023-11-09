import math
import os

import numpy as np

from src.readability_preprocessing.utils.csv import load_features_from_csv
from src.readability_preprocessing.sampling.stratified_sampling import (
    _extract_features, _calculate_similarity_matrix,
    _normalize_features, _parse_feature_output, sample,
    calculate_features)

RES_DIR = os.path.join(os.path.dirname(__file__), "../../res/")
CODE_DIR = RES_DIR + "code_snippets/"
JAR_OUTPUTS_DIR = RES_DIR + "jar_outputs/"
CSV_DIR = RES_DIR + "csv/"


def test_parse_feature_output():
    feature_string_file = JAR_OUTPUTS_DIR + "AreaShop/AddCommand.java/execute.txt"
    with open(feature_string_file) as f:
        feature_string = f.read()

    feature_data = _parse_feature_output(feature_string)

    assert isinstance(feature_data, dict)
    assert len(feature_data) == 110
    for feature_name, feature_value in feature_data.items():
        assert isinstance(feature_name, str)
        assert isinstance(feature_value, float)
        assert feature_value >= 0.0 or math.isnan(feature_value)


def test_extract_features():
    code_snippet = CODE_DIR + "AreaShop/AddCommand.java/execute.java"
    features = _extract_features(code_snippet)

    assert isinstance(features, dict)
    assert len(features) == 110
    for feature in features:
        assert isinstance(feature, str)
        assert isinstance(features[feature], float)
        assert features[feature] >= 0.0 or math.isnan(features[feature])


def test_extract_features_empty():
    code_snippet = CODE_DIR + "AreaShop/AreaShopInterface.java/debugI.java"
    features = _extract_features(code_snippet)

    assert isinstance(features, dict)
    assert len(features) == 110
    for feature in features:
        assert isinstance(feature, str)
        assert isinstance(features[feature], float)
        assert features[feature] >= 0.0 or math.isnan(features[feature])
    assert not all(math.isnan(feature) for feature in features.values())


def test_normalize_features():
    features = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ]

    normalized_features = _normalize_features(features)

    assert isinstance(normalized_features, np.ndarray)
    assert normalized_features.shape == (3, 3)
    for row in normalized_features:
        for value in row:
            assert 0.0 <= value <= 1.0


def test_calculate_cosine_similarity_matrix():
    features = np.array([
        [0.12309149, 0.20739034, 0.26726124],
        [0.49236596, 0.51847585, 0.53452248],
        [0.86164044, 0.82956135, 0.80178373]
    ])
    similarity_matrix = _calculate_similarity_matrix(features, metric="cosine")

    epsilon = 1e-8
    assert isinstance(similarity_matrix, np.ndarray)
    assert similarity_matrix.shape == (3, 3)
    assert abs(similarity_matrix[0, 0] - 1.0) < epsilon
    assert abs(similarity_matrix[1, 1] - 1.0) < epsilon
    assert abs(similarity_matrix[2, 2] - 1.0) < epsilon
    assert abs(similarity_matrix[0, 1] - similarity_matrix[1, 0]) < epsilon
    assert abs(similarity_matrix[0, 2] - similarity_matrix[2, 0]) < epsilon
    assert abs(similarity_matrix[1, 2] - similarity_matrix[2, 1]) < epsilon
    for row in similarity_matrix:
        for value in row:
            assert -1.0 <= value <= 1.0


def test_calculate_euclid_similarity_matrix():
    features = np.array([
        [0.12309149, 0.20739034, 0.26726124],
        [0.49236596, 0.51847585, 0.53452248],
        [0.86164044, 0.82956135, 0.80178373]
    ])
    similarity_matrix = _calculate_similarity_matrix(features, metric="euclidean")

    epsilon = 1e-8
    assert isinstance(similarity_matrix, np.ndarray)
    assert similarity_matrix.shape == (3, 3)
    assert abs(similarity_matrix[0, 0]) < epsilon
    assert abs(similarity_matrix[1, 1]) < epsilon
    assert abs(similarity_matrix[2, 2]) < epsilon
    assert abs(similarity_matrix[0, 1] - similarity_matrix[1, 0]) < epsilon
    assert abs(similarity_matrix[0, 2] - similarity_matrix[2, 0]) < epsilon
    assert abs(similarity_matrix[1, 2] - similarity_matrix[2, 1]) < epsilon
    for row in similarity_matrix:
        for value in row:
            assert 0 <= value


def test_calculate_jaccard_similarity_matrix():
    features = np.array([
        [0.12309149, 0.20739034, 0.26726124],
        [0.49236596, 0.51847585, 0.53452248],
        [0.86164044, 0.82956135, 0.80178373]
    ])
    similarity_matrix = _calculate_similarity_matrix(features, metric="jaccard")

    epsilon = 1e-8
    assert isinstance(similarity_matrix, np.ndarray)
    assert similarity_matrix.shape == (3, 3)
    assert abs(similarity_matrix[0, 0] - 1.0) < epsilon
    assert abs(similarity_matrix[1, 1] - 1.0) < epsilon
    assert abs(similarity_matrix[2, 2] - 1.0) < epsilon
    assert abs(similarity_matrix[0, 1] - similarity_matrix[1, 0]) < epsilon
    assert abs(similarity_matrix[0, 2] - similarity_matrix[2, 0]) < epsilon
    assert abs(similarity_matrix[1, 2] - similarity_matrix[2, 1]) < epsilon
    for row in similarity_matrix:
        for value in row:
            assert 0.0 <= value <= 1.0


def test_calculate_features():
    folder = "AreaShop/AddCommand.java"
    dir = os.path.join(CODE_DIR, folder)
    features = calculate_features(dir)

    assert isinstance(features, dict)
    assert len(features) == 4
    for paths in features.keys():
        assert isinstance(paths, str)
    for feature in features.values():
        assert isinstance(feature, dict)
        assert len(feature) == 110
        for feature_name, feature_value in feature.items():
            assert isinstance(feature_name, str)
            assert isinstance(feature_value, float)
            assert feature_value >= 0.0 or math.isnan(feature_value)


def test_sample():
    filename = "features.csv"
    dir = os.path.join(CSV_DIR, filename)
    num_stratas = 2
    snippets_per_stratum = 2
    features = load_features_from_csv(dir)
    stratas = sample(features, num_stratas=num_stratas,
                     snippets_per_stratum=snippets_per_stratum)

    assert isinstance(stratas, list)
    assert len(stratas) == num_stratas
    for stratum in stratas:
        assert isinstance(stratum, list) or isinstance(stratum, np.ndarray)
        assert len(stratum) <= snippets_per_stratum
        for snippet in stratum:
            assert isinstance(snippet, str)
            assert os.path.exists(snippet)
