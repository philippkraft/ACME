# -*- coding: utf-8 -*-
"""
Created on Aug 15 13:28 2017
@author(s): Florian U. Jehn

This file is used to start the construction of a predefined CMF model. The
user only has to provide the forcing data and the kind of techniques (
Distribution, objective function, etc.).

The structure is created in such a way, that there is always at least one
connection to the outlet.
"""
import acme.model_generators._lumped_CMF_model_template as template
import acme.model_generators._lookup as lookup
import acme.genetics.genetic as genetic
import datetime
import random


class LumpedCMFGenerator:
    def __init__(self, start_year,
                 end_year,
                 validation_time_span,

                 obj_func,
                 optimal_fitness,
                 Distribution,
                 algorithm,
                 et,

                 prec,
                 discharge,
                 t_mean,
                 t_min,
                 t_max,

                 max_age=50,
                 pool_size=10
                 ):
        """
        Sets everything up, ready to be solved.

        :param start_year: year for the start of the calibration period
        :param end_year: year for the end of the calibration period
        :param validation_time_span: time after end_year which should be
        used for calibration
        :param obj_func: the objective function that should be used (only
        the name is needed, all objective functions in spotpy are possible)
        :param Distribution: The way the parameters will be distributed (
        e.g. Weibull)
        :param et: Method for calculation of evapotranspiration
        """
        # Calibration/Validation stuff
        self.start_year = start_year
        self.end_year = end_year
        self.validation_time_span = validation_time_span
        # Get the functions and classes the match the user specified inputs.
        self.obj_func = lookup.get_obj_func(obj_func)
        self.optimal_fitness = optimal_fitness
        self.Distribution = lookup.get_distribution(Distribution)
        self.algorithm = lookup.get_algorithm(algorithm)
        self.et = lookup.get_evapotranspiration(et)
        # Forcing data
        self.data = {
            "prec": prec, 
            "discharge": discharge,
            "t_mean": t_mean,
            "t_min": t_min,
            "t_max": t_max
        }
        # Define gen set
        # This is done so widespread to make it more readable and also allow
        #  it later to check for what is in what.

        # "first_layer" is excluded, as a model wihout any storage makes no
        # sense
        self.storages = ["snow", "canopy", "second_layer",
                         "third_layer", "river"]
        self.connections = ["first_out", "first_river", "first_third",
                            "second_third", "second_river", "third_river"]
        self.snow_params = ["meltrate", "snow_melt_temp"]
        self.canopy_params = ["lai", "canopy_closure"]
        self.et_params = ["etv0", "fetv0"]
        self.first_layer_params = ["beta_first_out", "beta_first_river",
                                   "beta_first_second"]
        self.second_layer_params = ["beta_second_river", "beta_second_third"]
        self.third_layer_params = ["beta_third_river"]
        self.river_params = ["beta_river_out"]
        self.params = (self.snow_params + self.canopy_params +
                       self.et_params + self. first_layer_params +
                       self.second_layer_params + self.third_layer_params +
                       self.river_params)
        self.gene_set = self.storages + self.connections + self.params

        # Arguments for genetics behaviour
        self.max_age = max_age
        self.pool_size = pool_size
        
    def solve(self):
        """
        Starts the process of model selection.

        Calls the genetic file with all needed informations.
        :return: None, but writes the best found model to a file
        """
        # Make the needed variables available for the helper functions.
        data = self.data
        gene_set = self.gene_set
        obj_func = self.obj_func

        # Helper functions used as interface to genetic.

        def fn_create():
            return create(gene_set)

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, data, obj_func)

        def fn_mutate(genes):
            mutate(genes, fn_get_fitness)

        def fn_crossover(parent, donor):
            return crossover(parent, donor, fn_get_fitness)

        start_time = datetime.datetime.now()
        best = genetic.get_best(fn_get_fitness, None, self.optimal_fitness,
                                None, fn_display, fn_mutate, fn_create,
                                max_age=self.max_age,
                                pool_size=self.pool_size,
                                crossover=fn_crossover)
        while not self.optimal_fitness > best.fitness:
            pass

        write_best_model(best)


def get_fitness(genes, data, obj_func):
    """
    Calculates the fitness of a given genotype.
    :return:
    """
    ### First run the model with a row of default parameters for a few days and then cycle through it recurevily. Then check if a outlet is inside the model. If not assign it a fitness value of  a negative big number.
    ### If the model has a outlet let it then run normally.
    ### One could even make it this way, that this functions here just gets bkac the whole run table of the model and filters out the highest value for "like1" and returns it.


    #model = template.LumpedModelCMF()
    return 1


def display(candidate, start_time):
    """
    Display the current candidate and his fitness
    :param candidate:
    :param start_time:
    :return:
    """
    time_diff = datetime.datetime.now() - start_time
    print("Genes: {}\t\nFit: {}\tStrategy: {}\tTime: {}".format(
        " ".join(map(str, candidate.genes)),
        candidate.fitness, candidate.Strategy.name, time_diff))


def mutate(genes, gene_set):
    """
    Mutates a genome
    :param genes: genes of a given individual
    :param gene_set: all possible genes.
    :param fn_get_fitness:
    :return:
    """
    mutation_type = random.choice(["add", "del", "swap"])
    max_changes = 3
    if mutation_type == "add":
        for _ in random.randint(1, max_changes):
            # If the genes already contains all possible genes,
            # skip the process
            if set(genes) == set(gene_set):
                break
            while True:
                new_gene = random.choice(gene_set)
                # Check if the random choice to avoid adding it again
                if new_gene not in genes:
                    genes.append(new_gene)
                    break

    elif mutation_type == "del":
        for _ in random.randint(1, max_changes):
            # Pick a random genes
            genes = random.shuffle(genes)
            genes.pop()

    elif mutation_type == "swap":
        for _ in random.randint(1, max_changes):
            # Make a copy of the parent genes
            initial_genes = genes[:]
            # create a index for a random place in the parent genome
            index = random.randrange(0, len(genes))
            # take two random samples out of the gene set
            new_gene, alternate = random.sample(gene_set, 2)
            # replace the gene at index with another one, if it is randomly the
            # same, exchange it with the alternative.
            initial_genes[index] = (alternate if new_gene ==
                                    initial_genes[index]
                                    else
                                    new_gene)
    return


def crossover(first_parent, second_parent):
    """
    Performs a crossover between to genotypes.
    :return:
    """
    # Select two random points in the length of the parent and donor genome
    index_first_parent = random.randint(len(first_parent))
    index_second_parent = random.randint(len(second_parent))
    # Take all the genes from before the point from parent and all the genes
    # from behind the point from behind the point
    part_first_parent = first_parent[:index_first_parent]
    part_second_parent = second_parent[index_second_parent:]
    # Combine the parts
    child_genes = part_first_parent + part_second_parent
    # Create a set out of it to avoid duplicates
    # then turn it back to a list and return it
    child_genes = list(set(child_genes))
    return child_genes


def create(gene_set):
    """
    Creates a genotype after given rules.
    
    Allows creation in such a way, that a connection to the outlet is 
    guaranteed. 
    :param gene_set: all possible genes for a model
    :return: a genotype of a model
    """
    pass


def write_best_model(genes):
    """
    Writes the best model to a file.

    :param genes:
    :return:
    """
    pass