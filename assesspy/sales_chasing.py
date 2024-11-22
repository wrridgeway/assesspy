import warnings

import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF

from .utils import check_inputs


def _detect_chasing_cdf(
    estimate: list[int] | list[float] | pd.Series,
    sale_price: list[int] | list[float] | pd.Series,
    bounds: tuple[float, float] = (0.98, 1.02),
    gap: float = 0.03,
):
    check_inputs(estimate, sale_price)
    estimate = pd.Series(estimate, dtype=float)
    sale_price = pd.Series(sale_price, dtype=float)
    ratio: pd.Series = estimate / sale_price

    sorted_ratio = ratio.sort_values()

    # Calculate the CDF of the sorted ratios and extract percentile ranking
    cdf = pd.Series(ECDF(sorted_ratio)(sorted_ratio))

    # Calculate the difference between each value and the next value, the
    # largest difference will be the CDF gap
    diffs = cdf.diff().dropna()

    # Check if the largest difference is greater than the threshold and make
    # sure it's within the specified boundaries
    diff_loc = sorted_ratio.iloc[int(diffs.idxmax())]
    out = (diffs.max() > gap) & (
        (diff_loc > bounds[0]) & (diff_loc < bounds[1])
    )

    return out


def _detect_chasing_dist(
    estimate: list[int] | list[float] | pd.Series,
    sale_price: list[int] | list[float] | pd.Series,
    bounds: tuple[float, float] = (0.98, 1.02),
    gap: float = 0.03,
):
    check_inputs(estimate, sale_price)
    estimate = pd.Series(estimate, dtype=float)
    sale_price = pd.Series(sale_price, dtype=float)
    ratio: pd.Series = estimate / sale_price

    # Return the percentage of x within the specified range
    def pct_in_range(
        x: np.ndarray | pd.Series, min: float, max: float
    ) -> float:
        out = float(np.mean(((x >= min) & (x <= max))))
        return out

    # Calculate the ideal normal distribution using observed values from input
    ideal_dist = np.random.normal(np.mean(ratio), np.std(ratio), 10000)

    # Determine what percentage of the data would be within the specified
    # bounds in the ideal distribution
    pct_ideal = pct_in_range(ideal_dist, bounds[0], bounds[1])
    pct_actual = pct_in_range(ratio, bounds[0], bounds[1])

    return abs(pct_actual - pct_ideal) > gap


def detect_chasing(
    estimate: list[int] | list[float] | pd.Series,
    sale_price: list[int] | list[float] | pd.Series,
    bounds: tuple[float, float] = (0.98, 1.02),
    gap: float = 0.03,
    method="both",
):
    """
    Sales chasing is when a property is selectively reappraised to
    shift its assessed value toward its recent sale price. Sales chasing is
    difficult to detect. This function is NOT a statistical test and does
    not provide the probability of the given result. Rather, it combines two
    heuristic methods to roughly estimate if sales chasing has occurred.

    The first method (cdf) detects discontinuities in the cumulative
    distribution function (CDF) of the ratios of input values. Sales ratios
    that are not sales chased should have a fairly smooth CDF. Discontinuous
    jumps in the CDF, particularly around 1, may indicate sales chasing. This
    can usually be seen visually as a "flat spot" on the CDF.

    The second method (dist) uses the technique outlined in the
    `IAAO Standard on Ratio Studies`_ Appendix E, Section 4. It compares the
    percentage of real data within +-2% of the mean ratio to the percentage
    of data within the same bounds given a constructed normal distribution
    with the same mean and standard deviation. The intuition here is that
    ratios that are sales chased may be more "bunched up" in the center
    of the distribution.

    .. _IAAO Standard on Ratio Studies: https://www.iaao.org/media/standards/Standard_on_Ratio_Studies.pdf

    :param estimate:
        A list or ``pd.Series`` of estimated values.
        Must be the same length as ``sale_price``.
    :param sale_price:
        A list or ``pd.Series`` of sale prices.
        Must be the same length as ``estimate``.
    :param bounds:
        Default ``(0.98, 1.02)``. Tuple of two floats indicating the
        lower and upper bounds of the range of ratios to consider when
        detecting sales chasing. Setting this to a narrow band at the
        center of the ratio distribution prevents detecting false positives
        at the tails.
    :param gap:
        Default ``0.03``. Float tuning factor. For the CDF method, it sets the
        maximum percentage difference between two adjacent ratios. For the
        distribution method, it sets the maximum percentage point difference
        between the percentage of the data between the ``bounds`` in the real
        distribution compared to the ideal distribution.
    :param method:
        Default ``both``. String indicating sales chasing detection
        method. Options are ``cdf``, ``dist``, or ``both``.
    :type estimate: list[int] | list[float] | pd.Series
    :type sale_price: list[int] | list[float] | pd.Series
    :type bounds: tuple[float, float]
    :type gap: float
    :type method: str

    :return:
        A boolean value indicating whether or not the input values may
        have been sales chased.
    :rtype: bool

    :Example:

    .. code-block:: python

        import assesspy as ap
        import numpy as np
        from statsmodels.distributions.empirical_distribution import ECDF
        from matplotlib import pyplot

        # Generate fake data with normal vs chased ratios
        normal_ratios = np.random.normal(1, 0.15, 10000)
        chased_ratios = list(np.random.normal(1, 0.15, 900)) + [1] * 100

        # Plot to view discontinuity
        ecdf = ECDF(normal_ratios)
        pyplot.plot(ecdf.x, ecdf.y)
        pyplot.show()
        ap.detect_chasing(normal_ratios)

        ecdf = ECDF(chased_ratios)
        pyplot.plot(ecdf.x, ecdf.y)
        pyplot.show()
        ap.detect_chasing(chased_ratios)
    """
    if not (0 < gap < 1):
        raise ValueError("Gap must be a positive value less than 1.")
    if bounds[0] >= bounds[1]:
        raise ValueError(
            "Bounds must have the left value lower than the right value."
        )
    if len(estimate) < 30:
        warnings.warn(
            "Sales chasing detection can be misleading when applied to small "
            "samples (N < 30). Increase N or use a different test method."
        )

    if method == "cdf":
        out = _detect_chasing_cdf(estimate, sale_price, bounds, gap)
    elif method == "dist":
        out = _detect_chasing_dist(estimate, sale_price, bounds, gap)
    elif method == "both":
        out_cdf = _detect_chasing_cdf(estimate, sale_price, bounds, gap)
        out_dist = _detect_chasing_dist(estimate, sale_price, bounds, gap)
        out = out_cdf & out_dist
    else:
        raise ValueError("Method must be either 'cdf' or 'dist'")

    return out
