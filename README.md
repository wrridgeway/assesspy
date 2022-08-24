
<!-- README.md is generated from README.Rmd. Please edit that file -->

# AssessPy package <a href="https://gitlab.com/ccao-data-science---modeling/packages/assesspy/-/blob/main/docs/images/logo.png" align="right" height="139"/></a>

AssessPy is a software module for Python developed by the Cook County
Assessor’s (CCAO) Data Science Department. The
codebase for the CCAO’s CAMA system uses a wide range of functions
regularly, and packaging these functions streamlines and standardizes
their use. The CCAO is publishing this package to make it available to
assessors, reporters, and citizens everywhere.

For assessors, we believe that this package will reduce the complexity
of calculating ratio statistics and detecting sales chasing. We also
believe that reporters, taxpayers, and members of academia will find
this package helpful in monitoring the performance of local assessors
and conducting research.

For detailed documentation on included functions and data, [**visit the
full reference
list**](https://ccao-data-science---modeling.gitlab.io/packages/assesspy/reference/).

For examples of specific tasks you can complete with `assesspy`
functions, see the [**vignettes
page**](https://ccao-data-science---modeling.gitlab.io/packages/assesspy/articles/index.html).

## Installation

You can install the released version of `assesspy` directly from GitLab
by running the following R command after installing
[remotes](https://github.com/r-lib/remotes):

``` r
remotes::install_gitlab("ccao-data-science---modeling/packages/assesspy")

# Or, to install a specific version
remotes::install_gitlab("ccao-data-science---modeling/packages/assesspy@0.1")
```

Once it is installed, you can use it just like any other module. Simply
call `import assesspy` at the beginning of your script.
