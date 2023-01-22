import json
import math
import sys

import numpy as np
import pygad
import tqdm

import count_conflicts_cpp


def get_row(sudoku, i):
    return sudoku[i]


def get_col(sudoku, i):
    return [x[i] for x in sudoku]


def get_block(sudoku, i, j):
    return [sudoku[i * 3 + p][j * 3 + q] for p in range(3) for q in range(3)]


def get_gene_space(sudoku):
    res = []
    for i in range(len(sudoku)):
        for j in range(len(sudoku[0])):
            if sudoku[i][j] == 0:
                res.append(
                    list(set(range(1, 10)) - (
                        set(get_block(sudoku, i // 3, j // 3)).union(
                            set(get_row(sudoku, i))).union(
                                set(get_col(sudoku, j)))
                    ))
                )

    return res


def get_holes(sudoku):
    return [
        (i, j) for i in range(
            len(sudoku)
        ) for j in range(
            len(sudoku[0])
        ) if sudoku[i][j] == 0
    ]


def fill(sudoku, solution, holes):
    for i in range(len(solution)):
        sudoku[holes[i][0]][holes[i][1]] = int(solution[i])
    return sudoku


def count_conflicts_py(sudoku):
    conflicts = 0

    def get_conflicts(arr):
        _, counts = np.unique(arr, return_counts=True)
        return sum([math.comb(x, 2) for x in counts if x > 1])

    for i in range(len(sudoku)):
        conflicts += get_conflicts(get_row(sudoku, i))

    for i in range(len(sudoku[0])):
        conflicts += get_conflicts(get_col(sudoku, i))

    for i in range(len(sudoku) // 3):
        for j in range(len(sudoku[0]) // 3):
            conflicts += get_conflicts(get_block(sudoku, i, j))

    return conflicts


def fitness(solution, _):
    # Multiprocessing data share
    global sudoku, holes
    sudoku = fill(sudoku, solution, holes)

    return math.exp(-count_conflicts_cpp.count_conflicts(sudoku))


class AI:
    def __init__(
        self,
        plot_fitness=False,
        show_progress=False,
        print_final_conflicts=False,
        number_of_generations=2000,
        number_of_parent_mating=2,
        population=500,
        keep=1,
        number_of_processes=4
    ):
        self.number_of_generations = number_of_generations
        self.number_of_parent_mating = number_of_parent_mating
        self.population = population
        self.number_of_processes = number_of_processes
        self.plot_fitness = plot_fitness
        self.show_progress = show_progress
        self.keep = keep
        self.print_final_conflicts = print_final_conflicts
        pass

    def solve(self, problem):

        # Multiprocessing data share
        global sudoku, holes
        sudoku = json.loads(problem)['sudoku']
        holes = get_holes(sudoku)
        gene_space = get_gene_space(sudoku)

        ga_params = {
            'num_generations': self.number_of_generations,
            'num_parents_mating': self.number_of_parent_mating,
            'sol_per_pop': self.population,
            'keep_elitism': self.keep,
            'num_genes': len(gene_space),
            'gene_type': int,
            'gene_space': gene_space,
            'parent_selection_type': 'sss',
            'mutation_type': 'random',
            'crossover_type': 'single_point',
            'fitness_func': fitness,
            'stop_criteria': [
                'reach_1', f'saturate_{self.number_of_generations // 4}'
            ],
            'parallel_processing': ['process', self.number_of_processes]
        }

        if self.show_progress:
            with tqdm.tqdm(total=self.number_of_generations) as progress_bar:
                ga_instance = pygad.GA(
                    on_generation=lambda _: progress_bar.update(1),
                    **ga_params
                )
                ga_instance.run()
        else:
            ga_instance = pygad.GA(**ga_params)
            ga_instance.run()

        if self.plot_fitness:
            ga_instance.plot_fitness()

        solution, _, _ = ga_instance.best_solution()
        fill(sudoku, solution, holes)
        if self.print_final_conflicts:
            print(f'Conflicts: {count_conflicts_py(sudoku)}')
        return json.dumps({'sudoku': sudoku}, indent=2)


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as problem_file:
        print(AI(
            show_progress=True,
            plot_fitness=True,
            print_final_conflicts=True,
            population=1000,
            keep=1
        ).solve(problem_file.read()))
