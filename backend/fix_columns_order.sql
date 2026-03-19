-- Обновляем порядок колонок
UPDATE kanban_columns SET "order" = 1 WHERE title = 'Срочные задания';
UPDATE kanban_columns SET "order" = 2 WHERE title = 'Что улучшить?';
UPDATE kanban_columns SET "order" = 3 WHERE title = 'Задачи для игры';
UPDATE kanban_columns SET "order" = 4 WHERE title = 'Архив задач, чистить раз в 2 недели';
-- Inbox уже имеет order = 0
