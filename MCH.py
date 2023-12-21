from random import randint
from math import factorial, inf
from itertools import permutations as perm
import Methods

def MCH(deep, filename, metric=1, distance=1):
    '''Метод восхождения на холм. На вход получает глубину, расстояние для метрик,
     номер метрики от 1 до 5, имя файла для считывания таблицы с временами.
    Возвращает наилучшую перестановку.'''

    min_fine = inf                             # минимальное время
    random_permutations = []                   # список номеров восстанавливаемых перестановок
    min_permutation = None                     # оптимальная перестановка
    if distance < 1:
        distance = 1
    elif distance > 5:
        distance = 5
    if metric < 1:
        metric = 1
    elif metric > 5:
        metric = 5


    # чтение файла с временами
    times, tasks, deadlines = Methods.read_file(filename)  # матрица времен, количество работ, директивные сроки
    length_permutations = factorial(tasks)  # количество перестановок

    def random_permutation():
        '''Функция восстанавливает n-ую перестановку, номера которой нет в random_permutations.'''
        permutation = Methods.random_permutation(tasks)  # результирующая перестановка
        while permutation in random_permutations:
            permutation = Methods.random_permutation(tasks)

        random_permutations.append(permutation)
        return permutation

    def permutation_by_number(n):
        list_perm = list(range(1, tasks + 1))  # последовательность чисел
        permutation = []  # результирующая перестановка

        for i in range(tasks, 0, -1):
            index = n // factorial(i - 1)
            n = n % factorial(i - 1)
            permutation.append(list_perm.pop(index))

        return permutation

    def best_permunation_in_locality(permunations, deadlines):
        '''Функция возвращает из окрестности наилучшую перестановку, у которой наименьший штраф'''
        best_perm = permunations[0]
        min_fine = inf
        for permunation in permunations:
            fine = Methods.calc_fine(permutation, times, deadlines)
            if fine < min_fine:
                min_fine = fine
                best_perm = permunation

        return best_perm


    def transposition(permunation, distance):
        '''Транспозиционная метрика: перестановка чисел относительно начальной перестановки на расстоянии distance'''
        if distance < 1:
            return []

        result = []
        i = 0
        while i < len(permunation) - distance:
            j = i + distance
            while j < len(permunation):
                new_perm = list(permunation)
                # меняем местами числа перестановки по индексу
                new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
                result.append(tuple(new_perm))
                j += 1
            i += 1
        return result

    def lexicographic(permunation, distance):
        '''Лекцикографическая метрика: окрестность числа +- distance.
        Например для номера перестановки = 3 и distance = 1 будет 2 и 4.'''

        # получение номера по перестановке
        list_sort_permination = list(range(1, tasks + 1))    # последовательность чисел
        fact_perm = []

        for el in permunation:
            fact_perm.append(list_sort_permination.index(el))    # добавляем индекс элемента
            list_sort_permination.pop(list_sort_permination.index(el))    # удаляем элемент

        number = sum(fact_perm[i] * factorial(len(fact_perm) - i - 1) for i in range(len(fact_perm)))
        start = 0 if number - distance <= 0 else number - distance
        end = length_permutations - 1 if number + distance >= length_permutations else number + distance

        permutations = []  # окрестность
        for n in range(start, end + 1):
            if n != number:
                permutations.append(permutation_by_number(n))

        return permutations

    def chain(permunation, distance):
        '''Цепная перестановка: циклический сдвиг влево на distance, пока не получим исходную перестановку'''
        if distance >= len(permunation) or distance < 1:
            return []

        permunation = list(permunation)
        permunations = []
        for i in range(len(permunation) - 1):
            permunation = permunation[distance:] + permunation[:distance]
            permunations.append(permunation)
        return permunations

    def alphabet(permunation, distance):
        if distance < 1:
            return []
        part_perm = list(perm(permunation[-distance - 1:]))
        return [tuple(permunation[:-distance - 1]) + part_perm[i] for i in range(len(part_perm))][1:]

    def inversion(permunation, distance):
        if distance < 1:
            return []
        permunations = []
        i = 0
        while i + distance < len(permunation):
            _permunation = list(permunation)
            _permunation[i], _permunation[i + distance] = _permunation[i + distance], _permunation[i]
            permunations.append(_permunation)
            i += 1

        return permunations

    if metric == 1:
        func = transposition
    elif metric == 2:
        func = lexicographic
    elif metric == 3:
        func = chain
    elif metric == 4:
        func = alphabet
    elif metric == 5:
        func = inversion

    permutation = random_permutation()

    # метод восхождения на холм

    for i in range(deep):

        locality = func(permutation, distance)

        if len(locality) <= 0:
            break

        permutation = best_permunation_in_locality(locality, deadlines)
        fine = Methods.calc_fine(permutation, times, deadlines)
        if min_fine > fine:
            min_fine = fine
            min_permutation = permutation

    return min_permutation


#print(MCH(10, 'time.csv', metric=3, distance=4))


