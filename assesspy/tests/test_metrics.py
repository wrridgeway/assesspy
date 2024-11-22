import pytest as pt

import assesspy as ap


class TestMetrics:
    @pt.fixture(params=["cod", "prd", "prb", "mki", "ki"])
    def metric(self, request):
        return request.param

    @pt.fixture
    def metric_val(self, metric, ccao_data, quintos_data):
        if metric in ["mki", "ki"]:
            return getattr(ap, metric)(*quintos_data)
        return getattr(ap, metric)(*ccao_data)

    def test_metric(self, metric, metric_val):
        expected_values = {
            "cod": 17.81456901196891,
            "prd": 1.0484192615223522,
            "prb": 0.0009470721642262903,
            "mki": 0.794,
            "ki": -0.06,
        }
        assert pt.approx(metric_val, rel=0.02) == expected_values[metric]

    def test_numeric_output(self, metric_val):
        assert type(metric_val) is float

    def test_bad_input(self, metric, bad_input):
        with pt.raises(Exception):
            getattr(ap, metric)(*bad_input)

    def test_good_input(self, metric, good_input):
        try:
            result = getattr(ap, metric)(*good_input)
            assert type(result) is float
        except Exception as e:
            pt.fail(f"Unexpected exception {e}")

    def test_metric_met(self, metric, metric_val):
        if metric == "ki":
            pt.skip("Skipping test for 'ki' metric (ki_met does not exist)")
        expected_values = {
            "cod": False,
            "prd": False,
            "prb": True,
            "mki": False,
        }
        assert (
            getattr(ap, f"{metric}_met")(metric_val) == expected_values[metric]
        )
