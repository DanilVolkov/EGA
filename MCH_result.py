import csv
from random import randint
from math import factorial, inf
from itertools import permutations as perm
from datetime import datetime

filename = 'time.csv'              # имя файла для считывания таблицы с временами
filename_result_matrix = f'result_MCH_{datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.csv'       # имя файла для вывода результата
times = []                                 # матрица времен
min_fine = inf                             # минимальное время
tasks, length_permutations = 0, 0          # количество работ, количество перестановок
random_permutations = []                   # список номеров восстанавливаемых перестановок
min_permutation = None                     # оптимальная перестановка

deep = 10    # глубина поиска

# чтение файла с временами
with open(filename) as file:
    rows = csv.reader(file, delimiter=';')
    for row in rows:
        if not row:
            break
        times.append(list(map(int, row)))
    tasks = len(times[0])
    length_permutations = factorial(tasks)
    deadlines = list(map(int, next(rows)))

print(f'Глубина поиска: {deep}')
print('Директивные сроки: ', end='')
print(*deadlines, sep=' ')
print('Матрица времен:')
for i in range(len(times)):
    for j in range(len(times[0])):
        print(times[i][j], end=' ')
    print()

def random_permutation():
    '''Функция восстанавливает n-ую перестановку, номера которой нет в random_permutations.'''
    n = randint(0, length_permutations - 1)     # рандомная перестановка
    while n in random_permutations:
        n = randint(0, length_permutations - 1)
    random_permutations.append(n)

    return permutation_by_number(n)

def permutation_by_number(n):
    list_perm = list(range(1, tasks + 1))  # последовательность чисел
    permutation = []  # результирующая перестановка
    #number_perm = n
    #fact = []

    for i in range(tasks, 0, -1):
        index = n // factorial(i - 1)
        n = n % factorial(i - 1)
        permutation.append(list_perm.pop(index))
        # fact.append(index)

    # print(f'Факториальная запись: {fact[:-1]} для перестановки номер {number_perm}')

    return permutation


def calc_fine(permutation, deadlines):
    '''Функция считает штраф в текущей перестановке исходя их директивных сроков'''
    fines = []
    matrixX, matrixY = create_matrix(permutation)

    for i in range(len(permutation)):
        fine = matrixY[-1][i] - deadlines[permutation[i] - 1]
        fines.append(fine if fine > 0 else 0)

    return sum(fines)

def create_matrix(permutation):
    '''Создание матрицы для обработки работы'''

    # заполняем матрицу значениями по умолчанию
    matrixX = [[0] * len(permutation) for _ in range(len(times))]
    matrixY = [[0] * len(permutation) for _ in range(len(times))]


    for i in range(len(times)):
        for j in range(len(times[0])):
            matrixX[i][j] = max(matrixY[i][j - 1], matrixY[i - 1][j])
            # к времени старта прибавляем время от i станка и j элемента из перестановки
            matrixY[i][j] = matrixX[i][j] + times[i][permutation[j] - 1]

    # вывод матрицы для отладки
    # for i in range(len(times)):
    #     for j in range(len(times[0])):
    #         print(f'({matrixX[i][j]}, {matrixY[i][j]})', end=' ')
    #     print()

    return matrixX, matrixY

def best_permunation_in_locality(permunations, deadlines):
    '''Функция возвращает из окрестности наилучшую перестановку, у которой наименьший штраф'''
    best_perm = permunations[0]
    min_fine = inf
    for permunation in permunations:
        fine = calc_fine(permunation, deadlines)
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
    Например, для номера перестановки = 3 и distance = 1 будет 2 и 4.'''

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
    '''Алфавитная метрика: перестановки с конца до расстояния'''
    if distance < 1:
        return []
    part_perm = list(perm(permunation[-distance - 1:]))
    return [tuple(permunation[:-distance - 1]) + part_perm[i] for i in range(len(part_perm))][1:]

def inversion(permunation, distance):
    '''Инверсная метрика: количество инверсий между 2 перестановками'''
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

def graph_ganta(permutation, filename=''):
    matrixX, matrixY = create_matrix(permutation)
    # for i in range(len(times)):
    #     for j in range(len(times[0])):
    #         print(f'({matrixX[i][j]}, {matrixY[i][j]})', end=' ')
    #     print()

    for i in range(len(times)):
        res = ''
        for j in range(len(times[0])):
            if j - 1 < 0:
                res += ' ' * matrixX[i][j]
            elif matrixX[i][j] - matrixY[i][j - 1] > 0:
                res += ' ' * (matrixX[i][j] - matrixY[i][j - 1])
            res += str(permutation[j]) * (matrixY[i][j] - matrixX[i][j])
        if filename:
            with open(filename, 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_ALL)
                writer.writerow(res)
        else:
            print(res)

while True:
    print("\nВыберите одну из следующих метрик для алгоритма:")
    print("  1. Транспозиционная")
    print("  2. Лексикографическая")
    print("  3. Цепная")
    print("  4. Алфавитная")
    print("  5. Инверсная")
    print("  0. Выход")
    print("Метрика: ", end='')
    metric = int(input())

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
    elif metric == 0:
        exit()
    else:
        print("Данного метода нет.")
        continue

    print("Введите расстояние: ", end='')
    distance = int(input())

    if distance < 1:
        print("Расстояние должно быть больше 0")
        continue

    # метод восхождения на холм
    random_permutations = []  # список номеров восстанавливаемых перестановок
    permutation = random_permutation()
    #permutation = [5, 3, 8, 7, 2, 9, 1, 4, 6]
    min_fine = inf  # минимальное время
    min_permutation = None  # оптимальная перестановка

    # permutation = [2, 4, 3, 5, 6, 7, 1, 9, 8]    # для теста
    # permutations = perm((1, 2, 3, 4, 5, 6, 7, 8, 9))
    #print(f'Начальная перестановка: {permutation}')

    for i in range(deep):

        locality = func(permutation, distance)

        if len(locality) <= 0:
            break

        permutation = tuple(best_permunation_in_locality(locality, deadlines))
        fine = calc_fine(permutation, deadlines)
        print(f'Шаг: {i + 1}. Минимальный штраф: {min_fine}. Текущий штраф: {fine}. Текущая перестановка: {permutation}')
        if min_fine > fine:
            print(f'Произошла смена штрафа: {min_fine} -> {fine}')
            print(f'Произошла смена перестановки: {min_permutation} -> {permutation}')
            min_fine = fine
            min_permutation = permutation
        # else:
        #     break

    with open(filename_result_matrix, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow((min_fine, min_permutation))
        writer.writerow('')
        print(f'\nНаименьший штраф: {min_fine}. Порядок выполнения: {min_permutation}')
        print('\nМатрица выполнения работ: ')

        matrixX, matrixY = create_matrix(min_permutation)
        max_len = len(str(matrixY[-1][-1]))

        print(' ' * len(f"{len(times[0])} станок: "), end='')
        for i in range(len(times[0])):
            print(f'{i + 1} работа{" " * max_len}', end='')
        print()

        for i in range(len(times)):
            result = []
            print(f'{i + 1} станок: ', end='')
            for j in range(len(times[0])):
                result.append(f'({matrixX[i][j]}, {matrixY[i][j]})')
                print(f'{result[len(result) - 1]}'
                      f'{" " * (max(len(result[len(result) - 1]) + max_len, len(f"{j + 1} работа") + max_len) - min(len(result[len(result) - 1]), len(f"{j + 1} работа")))}',
                      end='')
            print()
            writer.writerow(result)
        writer.writerow('')

    print("\nГрафик Ганта:")
    graph_ganta(min_permutation, filename_result_matrix)
    graph_ganta(min_permutation)