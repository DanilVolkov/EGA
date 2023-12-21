import csv
from math import factorial, inf
from datetime import datetime

filename = 'time.csv'                                                                                   # имя файла для считывания таблицы с временами
filename_result_matrix = f'result_all_enumeration_{datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.csv'       # имя файла для вывода результата
times = []                                                                                              # матрица времен
min_fine = inf                                                                                          # минимальное время
tasks, length_permutations = 0, 0                                                                       # количество работ, количество перестановок
min_permutation = None                                                                                  # оптимальная перестановка


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

deep = factorial(tasks)   # глубина поиска


print(f'Глубина поиска: {deep}')
print('Директивные сроки: ', end='')
print(*deadlines, sep=' ')
print('Матрица времен:')
for i in range(len(times)):
    for j in range(len(times[0])):
        print(times[i][j], end=' ')
    print()


def create_permutation(n=0):
    '''Функция восстанавливает n-ую перестановку'''
    list_perm = list(range(1, tasks + 1))       # последовательность чисел
    permutation = []                            # результирующая перестановка

    for i in range(tasks, 0, -1):
        index = n // factorial(i - 1)
        n = n % factorial(i - 1)
        permutation.append(list_perm.pop(index))

    return permutation

def calc_fine(permutation, deadlines):
    '''Функция считает штраф в текущей перестановке исходя из директивных сроков'''
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
            # ко времени старта прибавляем время от i станка и j элемента из перестановки
            matrixY[i][j] = matrixX[i][j] + times[i][permutation[j] - 1]

    return matrixX, matrixY

def graph_ganta(permutation, filename=''):
    matrixX, matrixY = create_matrix(permutation)

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


# метод полного перебора
for i in range(deep):
    permutation = create_permutation(i)
    fine = calc_fine(permutation, deadlines)
    print(f'Шаг: {i + 1}. Текущий штраф: {fine}. Текущая перестановка: {permutation}')

    if min_fine > fine:
        print(f'Произошла смена штрафа: {min_fine} -> {fine}')
        print(f'Произошла смена перестановки: {min_permutation} -> {permutation}')
        min_fine = fine
        min_permutation = permutation

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




