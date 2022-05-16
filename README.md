# Backtest
Тестирует модель на исторических данных


# Подкюлючение
Скачайте bactester.py и выполните


photo1


# Инициализация
Класс backtester инициализируется историческими данными. Надо передать массив из путей до папки, где лежит дата. Например, у меня это выглядит так


photo2

# Запуск бэктеста
Для запуска надо вызвать метод test(), в который передаются параметры
depo - размер изначального депозита, доллары (по умолчанию 1000)
depo_rate - процент от депозита, который берется для сделки, % (по умолчанию 10)
stop_loss - процент на которую должна упасть цена, чтобы закрыть сделку, % (по умолчанию 5)
leverage - плечо (по умолчанию 1)
signal_files - массив путей до csv файлов с сигналами

photo3

Возвращается информация о сделках.
Начальный и конечный депозит
Абсолютная прибыль и прибыль в процентах
Минимальное значение депозита во время торговли
Минимальная просадка во время трейда и средняя просадка
Количество всех трейдов, в плюс и в минус
Коэффициент Шарпа (среднее значение делить на среднее отклонение)
График сделок, наложенных на цену актива
График изменения депозита

photo4
photo5
photo6

# multitest

Добавлена возможность сравнивать графики депозитов у нескольких различных прогонов на одном графике.
Надо запустить метод multitest с параметрами каждого теста, обернутых в массив. Пример ниже

photo7
photo8
