""" Application Programming Interface module

This file is part of patternomatic.

Copyright © 2020  Miguel Revuelta Espinosa

patternomatic is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

patternomatic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with patternomatic. If not, see <https://www.gnu.org/licenses/>.

"""
import time
from typing import Any, List, Tuple, Union

import pkg_resources
from spacy import load as spacy_load
from spacy.cli import download as spacy_download

from patternomatic.ge.population import Population
from patternomatic.ge.stats import Stats
from patternomatic.nlp.bnf import dynamic_generator as dgg
from patternomatic.settings.config import Config
from patternomatic.settings.log import LOG


def find_patterns(
    samples: List[str],
    configuration: Union[str, None] = None,
    spacy_language_model_name: Union[str, None] = None,
) -> List[Tuple[Any, ...]]:
    """
    Given some samples, this function finds optimized patterns to be used by the
    Spacy's Rule Based Matcher.

    Args:
        samples: List of strings from where to find common linguistic patterns
        configuration: (str) Optional configuration file path to to be loaded
            (Fallbacks to default configuration)
        spacy_language_model_name: (str) Optional valid Spacy Language Model
            (Fallbacks to Spacy's en_core_web_sm)

    Returns:
        List of patterns found and list of each pattern matching score against
            the samples.

    """
    LOG.info(f"Loading language model {spacy_language_model_name}...")
    if "en-core-web-sm" not in [d.project_name for d in pkg_resources.working_set]:
        LOG.info(
            f"patternomatic's default spaCy's Language Model not installed,"
            f" proceeding to install en_core_web_sm, please wait..."
        )
        spacy_download("en_core_web_sm")

    try:
        nlp = spacy_load(spacy_language_model_name)
    except OSError:
        LOG.warning(
            f"Model {spacy_language_model_name} not found, "
            "falling back to patternomatic's default language model: en_core_web_sm"
        )

        nlp = spacy_load("en_core_web_sm")

    LOG.info("Building Doc instances...")
    samples = [nlp(sample) for sample in samples]

    if isinstance(configuration, str):
        LOG.info(
            f"Setting up configuration from the following path: {configuration}..."
        )
        config = Config(config_file_path=configuration)
    else:
        config = Config()
        LOG.info(f"Existing Config instance found: {config}")

    stats = Stats()

    bnf_g = dgg(samples)

    LOG.info("Starting Execution...")
    for _ in range(0, config.max_runs):
        start = time.monotonic()
        p = Population(samples, bnf_g, stats)
        p.evolve()
        end = time.monotonic()
        stats.add_time(end - start)
        stats.calculate_metrics()

    LOG.info(f"Execution report {stats}")
    stats.persist()

    LOG.info("Best individuals for this execution:")
    stats.most_fitted_accumulator.sort(key=lambda i: i.fitness_value, reverse=True)
    for individual in stats.most_fitted_accumulator:
        LOG.info(f"{individual}")

    return list(
        zip(*[[i.fenotype, i.fitness_value] for i in stats.most_fitted_accumulator])
    )
