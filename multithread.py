# -*- coding: utf-8 -*-

try:  # Обрабатываем все возможные ошибки
    # Импортируем необходимые библиотеки
    from telethon import TelegramClient, sync, errors
    from time import sleep
    from lxml import html
    from functools import partial
    import multiprocessing as mp
    import requests, random, sys, traceback, re


    def scrabThePage(page_number, return_dict):  # Функции скрабинга комплиментов со страницы сайта с комплиментами
        print('https://datki.net/komplimenti/zhenshine/page/' + str(
            page_number) + '/')  # Сообщаем об начале скраблинга этой страницы
        page = requests.get(
            'https://datki.net/komplimenti/zhenshine/page/' + str(page_number) + '/')  # Получаем страницу
        tree = html.fromstring(page.content)  # Выстраиваем дерево блоков html
        # При помощи XPath-выражения получаем список всех комплиментов со страницы (все комплименты находятся в блоках <a> с атриюутом data-clipboard-text):
        return_dict[page_number] = (tree.xpath('//a[@class="post-copy btn"]/@data-clipboard-text'))


    def message(internal_compliments, internal_api_id, internal_api_hash):  # Функция отправки сообщения
        # Инициализируем подключение
        internal_client = TelegramClient('Compliments', internal_api_id, internal_api_hash)  # Задаем параметры клиента
        internal_client.start()  # Подключаемся
        rand_compl = random.choice(
            internal_compliments)  # Выбираем случайный комплимент из списка отфильтрованных по длине комплиментов
        internal_client.send_message(sendToUsername, rand_compl)  # Отправляем комплимент адресату
        internal_client.disconnect()  # Отключаемся после отправки сообщения
        print('ОТПРАВЛЕН КОМПЛИМЕНТ: ' + str(rand_compl))  # Сообщаем в
        # консоль об отправке комплимента


    if __name__ == '__main__':  # Если это основной процесс
        api_id = 0000000  # Telegram api_id
        api_hash = 'a9a9a9a9a9a9a9a9a9a9a9a9'  # Telegram api_hash
        defaultRecipient = 'vladimirpitun'  # Адресат по умолчанию
        defaultMinComplimentLength = '70'  # Минимальная длина комплимента по умолчанию

        jobs = []  # Коллекция параллельных процессов
        manager = mp.Manager()  # Мененджер библиотеки Multiprocessing
        compl_dict = manager.dict()  # Задаем переменную словаря менеджера

        print('Сбор комплиментов:', end='\n')  # Объявляем о начале сбора комплиментов
        i = 2  # Начинаем со второй страницы для большей скорости скраблинга - тк первая страница ведет на редирект и данные с нее получаюстя значительно дольше, чем с остальных страниц, то просто пропускаем ее
        while i <= 6:  # Всего на сайте 6 страниц с комплиментами
            proc = mp.Process(target=scrabThePage, args=(i, compl_dict))  # Создаем объект процесса
            i += 1  # Счетчик +1
            jobs.append(proc)  # Добавляем объект процесса в коллекцию параллельных процессов
            proc.start()  # Запускаем выполнение процесса
            # И так для каждой из 6 страниц, кроме первой. На выходе получим словарь с ключами в виде номеров страниц и значениями к каждому ключу в виде самих комплиментов типа String

        for proc in jobs:  # Дожидаемся завершения работы всех процессов
            proc.join()  # Ждем каждый из запущенных процессов, хранящихся в коллекции параллельных процессов

        all_compliments = []  # Коллекция, куда будем добавлять все комплименты со всех страниц
        i = 2  # Ключи в словаре начинаются с 2, тк мы пропустили первую страницу
        while i <= 6:  # Для каждой изстраниц в словаре, то есть от 2й до 6й...
            all_compliments.extend(
                compl_dict.get(i))  # Забираем в наш список комплиментов значения для каждой страницы из словаря
            i += 1  # Счетчик +1

        print('Сбор комплиментов... [OK]', end='\n\n')  # Сообщаем о том, что комплименты собраны

        mask = re.compile(
            '[a-zA-Z0-9_]')  # Задаем маску через функцию compile из библиотеки re для проверки того, что в введенном имени пользователя нет ничего, кроме маленьких и больших букв и цифр
        is_correct_input = False  # Переменная, говорящая нам о том, получили ли мы корректное значение от пользователя
        sendToUsername = 'empty'  # Объявляем переменную имени адресата, временно присваиваем ей значение 'empty'.
        # Объявление нужно для того, чтобы у функции было какое-то значение, чтобы ее можно было использовать в сравнени с другими переменными
        while (not is_correct_input) and (
        not sendToUsername == ''):  # Пока не получили корректное имя пользователя или пустое значение (то есть пользователь не ввел ничего, а просто нажал Enter)
            sendToUsername = input('Введите имя пользователя: ')  # Получаем имя адресата
            is_correct_input = mask.search(
                sendToUsername)  # Если имя адресата соответствует маске, значит search вернет True, которое запишется в переменную корректности введенного имени пользователя
            if (not is_correct_input) and (
            not sendToUsername == ''):  # Если введенное значение не корректно и не является пустым...
                print('Введенное имя пользователя содержит недопустимые символы [ERROR]',
                      end='\n\n')  # Выдаем сообщение о некорректном вводе

        # В случае введенного пустого значения, присваиваем юзернейму автозначение по умолчанию
        if (sendToUsername == ''):
            sendToUsername = defaultRecipient  # Используем значение по умолчанию
            print('Имя пользователя: ' + sendToUsername + ' [AUTO]',
                  end='\n\n')  # Сообщаем об использовании авто-значения
        else:  # Если до этого пользователь ввел какое-то корректное имя...
            print('Имя пользователя: ' + sendToUsername + ' [OK]',
                  end='\n\n')  # Сообщаем о том, что адресат назначен на основании введенного имени

        compliments = []  # Создаем список, куда будем добавлять подходящие по длине комплименты, чтобы потом отправлять случайно выбранные комплименты из этого списка
        while (len(compliments) == 0):  # Пока список отфильтрованных по длине комплиментов пуст
            mask = re.compile('[0-9]')  # Создаем маску для получения числа
            is_correct_input = False  # Переменная корректности ввода (как и в случае с вводом имени пользователя)
            min_compl_len = '0'  # Инициализируем переменную минимальной длины комплимента, временно присваивая ей 0
            while (not is_correct_input) and (
            not min_compl_len == ''):  # Пока пользователь не ввел корректную длину комплимента или не ввел пустое значение
                min_compl_len = input('Введите минимальную длину комплимента: ')  # Просим ввести мин длину комплимента
                is_correct_input = mask.search(
                    min_compl_len)  # Если минимальная длина задана корректно, в переменную корректности введенного значения запишется True
                if (not is_correct_input) and (
                not min_compl_len == ''):  # Если не введено корректного или пустого значения...
                    print('Введенное значение содержит недопустимые символы (должно содержать только цифры) [ERROR]',
                          end='\n\n')  # Выдаем сообщение об ошибке

            if (min_compl_len == ''):  # Если ничего не ввели...
                min_compl_len = defaultMinComplimentLength  # Используем значение по умолчанию
                print('Минимальная длина комплимента: ' + min_compl_len + ' [AUTO]',
                      end='\n\n')  # Сообщаем об использовании авто-значения
            else:  # если ввели что-то...
                print('Минимальная длина комплимента: ' + min_compl_len + ' [OK]',
                      end='\n\n')  # Сообщаем, что используем введенное значение

            # Отфильтруем комплименты, удалив те, что меньше, чем заданная пользователем минимальная длина
            for compliment in all_compliments:  # Для каждого комплимента из списка комплиментов
                if (len(compliment) >= int(
                        min_compl_len)):  # Проверяем: если длина меньше, чем заданная пользователем минимальная длина...
                    compliments.append(compliment)  # ... то удаляем комплимент из списка

            if (len(
                    compliments) == 0):  # Если мы так и не нашли ни одного комплимента, подходящего по введенной пользователем минимальной длине...
                print(
                    'Для указанной минимальной длины не найдено ни одного комплимента. Попробуйте уменьшить значение. [ERROR]',
                    end='\n\n')  # ... сообщаем об этом пользователю.
                # Далее переход в начало цикла, а далее - снова ввод нового значения, если ни один подходящий по длине  комплимент не был найден, либо продолжение программы, если хотя бы один подходящий по длине комплимент был найден

        print('Ожидание нажатия кнопки...', end='\n\n')  # Сообщаем об ожидании нажатия кнопки

        while True:  # Бесконечный цикл...
            input()  # При нажатии кнопки...
            message(compliments, api_id, api_hash)  # Отправляем комплимент с нашего аккаунта в телеграме

except KeyboardInterrupt:  # Исключение при становке пользователем
    print(
        'Завершено пользователем [OK]')  # Выводим сообщение о том, что программа завершена пользователем, стирая строку с символами Ctrl+C
except ValueError:  # Ошибка при попытке отправки сообщения пользователю, которому вы не можете отправлять сообщения
    print(
        'Возникла ошибка при попытке отправить сообщение указанному адресату [ERROR]')  # Выдаем соответствующее уведомление
except:  # Обрабатываем ошибки...
    print('Произошла неизвестная ошибка [ERROR]')  # Сообщение об ошибке
    print('\n=======ИНФОРМАЦИЯ ОБ ОШИБКЕ=========')  # Верхняя граница репорта об ошибке
    traceback.print_exc(limit=2, file=sys.stdout)  # Подробный репорт об ошибке и ее причинах
    print('========КОНЕЦ========')  # Конец репорта