# Воруем персидский
- выгруженный Новый Словарь в странном json формате
- код который я использовал

### структура словаря
```
{
Вход1: {
    transliteration: "Транслитерация"
    senses: [  # тут разные значения если слово многозначное
        {
            comments: ["помета1", ...],
            translations: [
                ("перевод1", "(скобочный контекст к нему)"),
                ...
                ]
        }, 
        ...
        ], 
    collocations: {  # тут скорее идиомы с лексемой из входа
        Идиома1: {
            comments: ["помета1", ...],
            translations: ["перевод1", ...]
            },
        Идиома2: ...,
        ...
        }
    },
Вход2: ...,
...
}
```
