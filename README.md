# Backtest
Тестирует модель на исторических данных


# Подкюлючение
Скачайте bactester.py и выполните

![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo1.png)


# Инициализация
Класс backtester инициализируется историческими данными. Надо передать массив из путей до папки, где лежит дата. Например, у меня это выглядит так


![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo2.png)

# Запуск бэктеста
Для запуска надо вызвать метод test(), в который передаются параметры

* depo - размер изначального депозита, доллары (по умолчанию 1000)

* depo_rate - процент от депозита, который берется для сделки, % (по умолчанию 10)

* stop_loss - процент на которую должна упасть цена, чтобы закрыть сделку, % (по умолчанию 5)

* leverage - плечо (по умолчанию 1)

* signal_files - массив путей до csv файлов с сигналами

![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo3.png)

Возвращается информация о сделках:

* Начальный и конечный депозит

* Абсолютная прибыль и прибыль в процентах

* Минимальное значение депозита во время торговли

* Минимальная просадка во время трейда и средняя просадка

* Количество всех трейдов, в плюс и в минус

* Коэффициент Шарпа (среднее значение делить на среднее отклонение)

* График сделок, наложенных на цену актива

* График изменения депозита

![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo4.png)
![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo5.png)
![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo6.png)

# multitest

Добавлена возможность сравнивать графики депозитов у нескольких различных прогонов на одном графике.
Надо запустить метод multitest с параметрами каждого теста, обернутых в массив. Пример ниже

![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo7.png)
![Image alt](https://github.com/danilalapokin/backtest/tree/main/screen/photo8.png)
