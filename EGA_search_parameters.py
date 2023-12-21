import csv

from MonteKarlo import MonteKarlo as mt
import random
import Methods
import matplotlib.pyplot as plt
from math import floor, inf, factorial


def copy_population(population):
    '''Копирование популяции'''
    return [el[:] for el in population]

def create_fines(population, times, deadlines):
    '''Добавление приспособленности к индивидам'''
    return list(map(lambda el: Methods.calc_fine(el, times, deadlines), population))

def create_start_populations(population_size, filename):
    '''Создание начальной популяции'''
    population = []
    while len(population) < population_size:
        p = mt(10, filename)

        if p not in population:
            population.append(p)

    return population

def panmixia(population):
    '''Случайный выбор родительской пары'''
    random.shuffle(population)
    return [(population[i], population[i + 1]) for i in range(0, len(population), 2)]

def breeding(population, method):
    '''Предпочтение отдается генетически похожим или различным особям'''
    parents = []
    while len(population) > 0:
        max_hamming_distance = -1
        min_hamming_distance = inf
        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                hamming_distance = sum(1 for gen in range(len(population[i])) if population[i][gen] != population[j][gen])
                if method:  # наиболее близкие особи
                    if hamming_distance < min_hamming_distance:
                        min_hamming_distance = hamming_distance
                        p1_index, p2_index = i, j
                else:  # наиболее различные особи
                    if hamming_distance > max_hamming_distance:
                        max_hamming_distance = hamming_distance
                        p1_index, p2_index = i, j

        parents.append((population[p1_index], population[p2_index]))
        population.pop(p1_index)
        population.pop(p2_index - 1)

    return parents

def associative_crossing(population, method):
    '''При образовании брачных пар выбираются наиболее приспособленные особи или
    сильно отличающиеся по степени приспособленности'''
    parents = []
    # сортируем родителей по приспособленности
    p = list(map(lambda p: p[0], sorted(population, key=lambda x: x[1])))
    if method:  # положительное ассоциативное скрещивание (наиболее приспособленные пары)
        for i in range(0, len(p) - 1, 2):
            parents.append((p[i], p[i + 1]))
    else:  # отрицательное ассоциативное скрещивание (наиболее отличающиеся по степени приспособленности пары)
        for i in range(len(p) // 2):
            parents.append((p[i], p[len(p) - i - 1]))

    return parents

def ordinal(parent1, parent2):
    '''Порядковый кроссовер'''

    descendant1, descendant2, descendants_result = [], [], []

    def ox(parent, descendant, descendant_temp, split):
        for p in parent:
            if split <= len(descendant) < len(parent) - split:
                descendant.extend(descendant_temp)
            if p not in descendant_temp:
                descendant.append(p)
        return descendant

    split = len(parent1) // 3
    descendant_temp1 = tuple(parent1[split:-split])
    descendant_temp2 = tuple(parent2[split:-split])
    descendant1 = ox(parent2, descendant1, descendant_temp1, split)
    descendant2 = ox(parent1, descendant2, descendant_temp2, split)
    descendants_result.extend((descendant1, descendant2))

    return descendants_result

def partial_display(parent1, parent2):
    '''Кроссовер частичного отображения'''
    descendant1, descendant2, descendants_result = [], [], []

    def pmx(parent, descendant, descendant_temp, split, display_start, display_end):
        for i in range(len(parent)):
            if split <= len(descendant) < len(parent) - split:
                descendant.extend(descendant_temp)  # секция копируется полностью
            if i < split or i >= len(parent) - split:
                if parent[i] in display_start:
                    descendant.append(display_end[display_start.index(parent[i])])  # копируем отображенный элемент
                else:
                    descendant.append(parent[i])  # копируем исходный элемент
        return descendant

    split = len(parent1) // 3
    descendant_temp1 = tuple(parent1[split:-split])
    descendant_temp2 = tuple(parent2[split:-split])
    d_temp1, d_temp2 = parent1[split:-split], parent2[split:-split]
    display_start, display_end = [], []

    # составляем пары отображений
    while len(d_temp1) > 0:
        p1, p2 = d_temp1[0], d_temp2[0]
        d_temp1.pop(0)
        d_temp2.pop(0)
        while p2 in d_temp1:
            index = d_temp1.index(p2)
            p2 = d_temp2[index]
            d_temp1.pop(index)
            d_temp2.pop(index)
        display_start.append(p1)
        display_end.append(p2)

    descendant1 = pmx(parent2, descendant1, descendant_temp1, split, display_start, display_end)
    descendant2 = pmx(parent1, descendant2, descendant_temp2, split, display_end, display_start)

    descendants_result.extend((descendant1, descendant2))

    return descendants_result

def cyclic(parent1, parent2):
    '''Циклический кроссовер'''
    # формируем циклы из индексов
    indexes, cycles, descendants_result = [], [], []
    for i in range(len(parent1)):
        if i not in indexes:
            cycles.append([i])
            indexes.append(i)
            gen = parent2[i]
            while gen in parent1:
                index = parent1.index(gen)
                if index in indexes:
                    break
                indexes.append(index)
                gen = parent2[index]
                cycles[len(cycles) - 1].append(index)
    cycles = [el for el in cycles if len(el) > 1]

    # формируем списки приоритета родителей по количеству циклов
    variants = [tuple(map(lambda x: int(x), f"{str(bin(el))[2:]:0>{len(cycles)}}")) for el in
                range(1, factorial(len(cycles)) + 1)]

    # комбинируем циклические подстановки
    for variant in variants:
        descendant1 = []
        for i in range(len(parent1)):
            f = True
            for c in range(len(cycles)):
                if i in cycles[c] and variant[c] != 0:
                    descendant1.append(parent2[i])
                    f = False
                    break
            if f:
                descendant1.append(parent1[i])
        descendants_result.append(descendant1)

    # при одинаковых родителях, количество наследников = 1, поэтому дублируем его
    if len(descendants_result) == 1:
        descendants_result.append(descendants_result[0][:])

    return descendants_result

def gene_mutation(descendant):
    '''Точечная мутация'''
    gen1 = random.randint(0, len(descendant) - 2)
    gen2 = gen1 + 1
    descendant[gen1], descendant[gen2] = descendant[gen2], descendant[gen1]
    return descendant

def saltation(descendant):
    '''Сальтация'''
    gen1 = random.randint(0, len(descendant) // 2)
    gen2 = random.randint(gen1 + 2, len(descendant) - 1)
    descendant[gen1], descendant[gen2] = descendant[gen2], descendant[gen1]
    return descendant

def inversion(descendant):
    '''Инверсия'''
    index = len(descendant) // 3
    gen1 = index
    gen2 = len(descendant) - index
    descendant[gen1:gen2] = reversed(descendant[gen1:gen2])
    return descendant

def translocation(descendant):
    '''Транслокация'''
    index = len(descendant) // 3
    gen1 = index
    gen2 = len(descendant) - index
    trans = lambda descendant_part: descendant_part[-1:] + descendant_part[:-1]

    if (len(descendant[:gen1])) == 1:
        descendant[:gen1], descendant[gen2:] = \
            descendant[gen2:], descendant[:1]
    else:
        descendant[:gen1] = trans(descendant[:gen1])
        descendant[gen2:] = trans(descendant[gen2:])

    return descendant

def reverse_fines(fines):
    '''Переворачиваем штрафы. Из максимального делаем минимальтный и наоборот'''
    max_fine = max(fines)
    reverse_fine = [max_fine - el + 10 for el in fines]
    return reverse_fine

def proportional_scheme(population):
    '''Процорциональная схема селекции'''
    fines = reverse_fines(list(map(lambda el: el[1], population)))
    return [(population[i][0], fines[i]) for i in range(len(population))]

def linear_ranking_scheme(population, n_min=0.5, n_max=1.5):
    '''Линейно-ранговая схема селекции'''
    linear_func = lambda n, m, r, l: n + (m - n) * r / (l - 1)
    dict_p = {el[1]: el[0] for el in population}
    sorted_p = list(zip(sorted(population, key=lambda el: el[1], reverse=True), range(1, len(population) + 1)))
    ranks = [(sorted_p[i][0][0],
              linear_func(n_min, n_max, (sorted_p[i - 1][1] if i > 0 else 0),
                          len(population)) / len(population) * 1000) for i in range(len(population))]

    return ranks

def beta_tournament(population, p_size, fights):
    '''Бета-турнир'''
    new_population = []
    for i in range(p_size):
        fighters = []
        for _ in range(fights):
            fighters.append(population[random.randint(0, len(population) - 1)])
        best_solution = min(fighters, key=lambda x: x[1])
        new_population.append(best_solution[0])
        population.pop(population.index(best_solution))
    return new_population

def roulette_without_return(population, p_size):
    '''Рулетка без возвращения'''
    new_population = []
    fines = [el[1] for el in population]
    sum_fines = sum(fines)

    for i in range(p_size):
        sum1 = 0
        sum2 = fines[0]
        roulette = random.randint(1, int(sum_fines))
        for j in range(len(fines)):  # длина не должна быть -1, так как алгоритм не выйдет за границы массива
            if sum1 < roulette <= sum2:
                new_population.append(population[j][0])
                fines[j] = 0
                sum_fines = sum(fines)
                break
            sum1 = sum2
            sum2 += fines[j + 1]

    return new_population

def universal_choice(population, p_size):
    '''Универсальный выбор'''
    new_population = []
    fines = [el[1] for el in population]
    sum_fines = sum(fines)

    split = sum_fines // p_size
    roulettes = []
    for i in range(p_size):
        roulettes.append(random.randint(split * i + 1, min(split * (i + 1), sum_fines)))

    sum1 = 0
    sum2 = fines[0]
    for i in range(len(fines)):
        for roulette in roulettes:
            if sum1 < roulette <= sum2:
                new_population.append(population[i][0])
        if len(new_population) == p_size:
            break
        sum1 = sum2
        sum2 += fines[i + 1]

    return new_population

def partial_return_selection(population, p_size):
    '''Выбор с частичным возвращением'''
    new_population = []
    fines = [el[1] / 10 for el in population]
    sum_fines = sum(fines)

    for i in range(p_size):
        sum1 = 0
        sum2 = fines[0]
        roulette = random.random() * sum_fines
        for j in range(len(fines)):  # длина не должна быть -1, так как алгоритм не выйдет за границы массива
            if sum1 < roulette <= sum2:
                new_population.append(population[j][0])
                fines[j] = floor(fines[j] - 1)
                sum_fines = sum(fines)
                break
            sum1 = sum2
            try:
                sum2 += fines[j + 1]
            except:
                print('ok')

    return new_population

# для теста!!!
RANDOM_SEED = 100
random.seed(RANDOM_SEED)

# Обязательные параметры
filename = 'time.csv'
deep = 40
population_size = 14
probability_mutation = 0.2
fights = 5
elite_selection = True
selection_scheme = 3
algorithm_copy = 1  # при пропорциональной схеме можно выбрать только 1 или 2
choose_parents_method = 1
breeding_method = True  # 1 или 2
associative_crossing_method = True  # 1 или 2
crossover_method = 1
mutation_method = 1
macromutation_method = 1
scaling = False

total_start_population = create_start_populations(30, filename)


def ega(filename, deep, population_size, probability_mutation, fights, elite_selection,
        algorithm_copy, choose_parents_method, breeding_method, associative_crossing_method,
        crossover_method, mutation_method, macromutation_method, scaling):

    # Входные переменные
    mean_fitness = []
    max_fitness = []
    times, _, deadlines = Methods.read_file(filename)
    population = copy_population(total_start_population[:population_size])

    # Для теста!!!
    #print(f'Стартовая популяция: {population}')

    for i in range(deep):

        # выбор родительской пары
        parents = None
        if choose_parents_method == 1:
            parents = panmixia(copy_population(population))
        elif choose_parents_method == 2:
            parents = breeding(copy_population(population), breeding_method)
        else:
            parents = associative_crossing(copy_population(list(zip(population, create_fines(population, times, deadlines)))),
                                           associative_crossing_method)
        #print(f'родители: {parents}')

        # кроссовер - формирование потомков (перемешивание генов)
        crossover = None
        if crossover_method == 1:
            crossover = ordinal
        elif crossover_method == 2:
            crossover = partial_display
        else:
            crossover = cyclic

        descendants = []
        for parent1, parent2 in copy_population(parents):
            descendants.extend(crossover(parent1, parent2))
        #print(f'потомки: {descendants}')

        # мутация - изменение генов потомков
        mutation = None
        if mutation_method == 1:
            mutation = gene_mutation
        elif mutation_method == 2:
            if macromutation_method == 1:
                mutation = saltation
            elif macromutation_method == 2:
                mutation = inversion
            else:
                mutation = translocation

        mutants = []
        for descendant in descendants:
            if random.random() < probability_mutation:
                if mutation_method == 3:
                    mutants.append(*create_start_populations(1, filename))  # дополнение
                else:
                    mutants.append(mutation(descendant[:]))
        #print(f'мутанты: {mutants}')

        # формируем популяцию из старой популяции, потомков и мутантов
        new_population = [*copy_population(population), *copy_population(descendants), *copy_population(mutants)]

        # масштабирование
        if scaling:
            # удаляем дубликаты из популяции
            new_population = [new_population[0][:],
                              *filter(lambda el: el not in (*new_population[:new_population.index(el)], *new_population[new_population.index(el) + 1:]), new_population[1:])]

            # если популяция меньше, чем размер популяции, то добавляем недостающие рандомно
            if len(new_population) <= population_size:
                new_population.extend(create_start_populations(population_size - len(new_population) + 2, filename))

        # добавляем приспособленность
        new_population = list(zip(new_population, create_fines(new_population, times, deadlines)))
        boss = None
        population.clear()

        # независимо от схемы селекции копируем самую приспособленную особь
        if elite_selection:
            boss = min(new_population, key=lambda x: x[1])
            new_population.pop(new_population.index(boss))
            population.append(boss[0][:])

        # изменяем приспособленность в зависимости от схемы
        if selection_scheme == 1:
            new_population = proportional_scheme(new_population)
        elif selection_scheme == 2:
            new_population = linear_ranking_scheme(new_population)
        elif selection_scheme == 3:  # при бета-турнире сразу создаем популяцию без алгоритмов копирования
            population.extend(copy_population(beta_tournament(new_population, population_size - int(elite_selection), fights)))

        # выбираем алгоритм копирования
        algorithm = None
        if algorithm_copy == 1:
            algorithm = roulette_without_return
        elif algorithm_copy == 2:
            algorithm = universal_choice
        else:
            algorithm = partial_return_selection

        if selection_scheme != 3:
            population.extend(copy_population(algorithm(new_population, population_size - int(elite_selection))))


        # подсчитываем максимальную и среднюю приспособленность
        fitness = create_fines(population, times, deadlines)
        mean_fitness.append(sum(fitness) / population_size)
        max_fitness.append(min(fitness))
        # print(f'{i + 1} Макс. присп: {max_fitness[i]}, Средняя присп: {mean_fitness[i]}')
        # print()

    if int(max_fitness[len(max_fitness) - 1]) == 100:
        with open('result_Monte_Karlo.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow((deep, population_size, choose_parents_method, breeding_method, associative_crossing_method,
                             crossover_method, mutation_method, macromutation_method, probability_mutation, algorithm_copy,
                             selection_scheme, elite_selection, fights, scaling, max_fitness[len(max_fitness) - 1], mean_fitness[len(mean_fitness) - 1]))
        print('yes!')
        # print(f'Глубина: {deep}, '
        #       f'Размер популяции: {population_size}, '
        #       f'Метод выбора родителей: {choose_parents_method}, '
        #       f'Бридинг: {breeding_method}, '
        #       f'Количественный выбор: {associative_crossing_method}, '
        #       f'Схема кроссовера: {crossover_method}, '
        #       f'Метод мутации: {mutation_method}, '
        #       f'Макромутация: {macromutation_method}, '
        #       f'Вероятность мутации: {probability_mutation}, '
        #       f'Алгоритм копирования: {algorithm_copy}, '
        #       f'Схема селекции: {selection_scheme}, '
        #       f'Элитарная схема: {elite_selection}, '
        #       f'Кол-во особей в турнире: {fights}, '
        #       f'Масштабирование: {scaling}, '
        #       f'Макс. присп: {max_fitness[len(max_fitness) - 1]}, '
        #       f'Средняя присп: {mean_fitness[len(mean_fitness) - 1]}')

        # для проверки!!!
        #print(*fitness)

    # plt.plot(max_fitness, color='red')
    # plt.plot(mean_fitness, color='green')
    # plt.xlabel('Поколение')
    # plt.ylabel('Макс/средняя приспособленность')
    # plt.title('Зависимость макс и средней присп. от поколения')
    # plt.show()

with open('result_Monte_Karlo.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(('Метод выбора родителей', 'Бридинг', 'Количественный выбор',
                     'Схема кроссовера', 'Метод мутации', 'Макромутация', 'Вероятность мутации', 'Алгоритм копирования',
                     'Схема селекции', 'Элитарная схема', 'Кол-во особей в турнире', 'Масштабирование', 'Макс. присп', 'Средняя присп'))

# for deep in range(40, 41):
#     for population_size in range(14, 15):
#         for probability_mutation in range(1, 10):
#             for elite_selection in range(2):
#                 #for scaling in range(2):
#                     for fights in range(3, 11):

for i in range(1, 100):
    RANDOM_SEED = i
    random.seed(RANDOM_SEED)
    print(f'Шаг {i}: ', end='')
    total_start_population = create_start_populations(30, filename)
    ega(filename, deep, population_size, probability_mutation / 10, fights, bool(elite_selection),
        algorithm_copy, choose_parents_method, bool(breeding_method),
        bool(associative_crossing_method),
        crossover_method, mutation_method, macromutation_method, bool(scaling))
                        # for choose_parents_method in range(1, 4):
                        #     for breeding_method in range(2):
                        #         for associative_crossing_method in range(2):
                        #             for crossover_method in range(1, 4):
                        #                 for mutation_method in range(1, 4):
                        #                     for macromutation_method in range(1, 4):
                        #                         for fights in range(3, 11):
                        #                             for selection_scheme in range(1, 4):
                        #                                 for algorithm_copy in range(1, 4):







