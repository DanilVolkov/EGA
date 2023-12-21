from math import inf
import Methods

def MonteKarlo(deep, filename):
    '''Метод Монте-Карло. На вход получает глубину поиска и имя файла. Возвращает наилучшую перестановку'''

    min_fine = inf                                                                                          # минимальное время
    random_permutations = []                                                                                # список номеров восстанавливаемых перестановок
    min_permutation = None                                                                                  # оптимальная перестановка

    # чтение файла с временами
    times, tasks, deadlines = Methods.read_file(filename)  # матрица времен, количество работ, директивные сроки


    def random_permutation():
        '''Функция восстанавливает n-ую перестановку, номера которой нет в random_permutations.'''
        permutation = Methods.random_permutation(tasks) # результирующая перестановка
        while permutation in random_permutations:
            permutation = Methods.random_permutation(tasks)

        random_permutations.append(permutation)
        return permutation

    # метод Монте-Карло
    for i in range(deep):
        permutation = random_permutation()
        fine = Methods.calc_fine(permutation, times, deadlines)

        if min_fine > fine:
            min_fine = fine
            min_permutation = permutation

    return min_permutation


#print(MonteKarlo(10, 'time.csv'))


