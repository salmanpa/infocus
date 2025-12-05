# System Diagrams and Frontend Concepts

Ниже — набор текстовых схем и примерных фронтенд-макетов, собранных по мотивам предоставленных иллюстраций. Все схемы в формате Mermaid, чтобы их можно было быстро просматривать в Markdown или конвертировать в изображения.

## 1. Общий контур сервиса
```mermaid
graph TD
    User[Пользователь] -->|делится настройками| SharingHub[Хаб обмена ссылками]
    User -->|читает| FriendsFeed[Общий стрим с друзьями]
    FriendsFeed -->|агрегация| NewsAggregators[Агрегаторы новостей]
    NewsAggregators -->|подписки| BaseSources[База источников]
    BaseSources -->|обновления| NewsAggregators
    NewsAggregators -->|черновики| Drafts[Черновики постов]
    Drafts -->|публикация| FriendsFeed
    Drafts -->|передать на доработку| AIEditor[AI Editor]
    AIEditor -->|генерация/улучшение| Drafts
    SharingHub -->|ссылки и промпты| PostRoutes[Входящие ссылки/посты]
    PostRoutes -->|фильтрация| AIEditor
    PostRoutes -->|добавить в ленту| FriendsFeed
```

## 2. Конвейер работы с ссылкой/постом
```mermaid
graph LR
    Input[Ссылка или пост] --> Filter[Фильтр/верификация]
    Filter --> Enrich[LLM/кластеризация тем]
    Enrich --> DraftGen[Генератор черновиков]
    DraftGen --> Suggestions[Подсказки стиля/тона]
    Suggestions --> Publish[Публикация в ленту]
    Filter -->|отклонено| Trash[Отклоненные]
```

## 3. Управление источниками и подписками
```mermaid
graph TD
    SourcesBase[База источников] --> Categories[Категории/теги]
    Categories --> Search[Поиск/фильтры]
    Search --> AddSource[Кнопка «Добавить»]
    AddSource --> UserLists[Пользовательские подборки]
    UserLists --> Aggregators[Агрегаторы новостей]
    Aggregators --> Timeline[Ленты/подборки]
```

## 4. Фронтовые блоки (каркасные схемы)
```mermaid
graph TD
    Home[Лента] --> Filters[Фильтры: дата, источник, тон]
    Home --> DraftPane[Панель черновика]
    Home --> AggregatorsList[Блок «Агрегаторы»]
    Home --> FriendsStream[Блок «Общий стрим»]
    DraftPane --> Actions[Редактировать / Отправить в AI / Публиковать]
    AggregatorsList --> SourceBase[База источников]
    FriendsStream --> Share[Поделиться с друзьями]
```

## 5. Пример фронтенд-макета
Ниже — быстрый HTML/CSS-шаблон в том же стиле, что на схеме «Агрегат новостей». Его можно открыть локально (файл лежит в `examples/front-mockups/news_aggregator.html`) и доработать под реальный стек.

- Левая колонка — фильтры и статус подборки.
- Центральная колонка — список агрегаторов и превью постов.
- Правая колонка — черновик и действия публикации.

В шаблоне уже размечены кнопки «Отправить в AI», «Сделать» (генерация), «Опубликовать» и «Поделиться с друзьями».
