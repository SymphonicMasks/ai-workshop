# Services
### Ml Service
Сервис для работы с моделями машинного обучения в рамках задачи транскрипции аудиофайлов.

Для сборки запуска контейнера команда

```bash
docker-compose up -d
```

Она соберёт Docker-образ, а затем запустит контейнер.

После успешного запуска контейнера приложение будет доступно на http://localhost:8080.

Для проверки доступности контейнера 

```bash
curl http://localhost:8080/version
```


### Chat Service
Сервис для работы с LLM моделью для генерации фидбэка на основе MIDI информации.

### Web Service
Просто сервис, который позволит нам наглядно и просто тестировать наши алгоритмы.

--- 

#### Полезные ссылки
- [Music Transcription](https://paperswithcode.com/task/music-transcription)
- [pretty_midi](https://craffel.github.io/pretty-midi/)
- [music21](https://www.music21.org/music21docs/)
- [mistral](https://console.mistral.ai/home)
