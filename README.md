# ИАД
## ЛАБОРАТОРНАЯ РАБОТА №1

Телефонный справочник сделан в виде бота в телеграм.

https://t.me/IAD_LAB1_BOT

Стек технологий: Python3.8/aiogram/redis/postgreSQL/Tortoise-ORM
Приложение полностью асинхронное.

### Обязательный функционал

✅ Просмотр всех записей справочника: вывод всего справочника так, чтобы было читабельно.\n
✅ Поиск по справочнику.Поиск может осуществляться по любому из полей, а также по нескольким полям одновременно (например, найти запись с именем «А» и фамилией «Б»).В результате поиска должны быть выведены найденные записи со значением полей.
✅ Добавление новой записи. NB:Обязательна проверка на то, что такая запись не содержится в справочнике(по уникальному идентификатору).Если такая запись уже содержится в справочнике, сообщить обэтом пользователю и предложить: изменить существующую запись, изменить (Имя, Фамилия) новой записи или вернуться к выбору команды.NB:При вводе Имени и Фамилии обязательна автозамена первой буквы на заглавную.
✅ Удаление записи из справочника по Имени и ФамилииИзменение любого поляв определенной записи справочника
✅ Вывод возраста человека (записи) по Имени и Фамилии

### Дополнительный функционал

🚫 Возможность добавления несколько номеров телефона для одной записи с категоризацией: мобильный, рабочий, домашний и т.д.oУдаление по номеру телефона.NB: обязательна проверка на наличие нескольких записей с таким номером. Предоставить выбор пользователю,какую именно запись или несколько удалить.
✅ Поиск и вывод записей по дате рождения (день и месяц, год не учитывается).
✅ Просмотр всех записей (только поля Имя и Фамилия), у которых день рождения в ближайший месяц (30 дней). 
🚫 Просмотр всех записей, которые старше / младше / ровно Nлет (Nзадаётся пользователем).
✅ Дополнительные возможности программы и расширение функционала. От добавления новых полей и функций работы с ними, до графического интерфейса и использования базы данных для хранения словаря.

Демонстрация работы:
https://youtu.be/JVP4zg-wiUY

