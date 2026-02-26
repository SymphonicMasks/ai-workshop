<p align="center">
  <img src="https://github.com/user-attachments/assets/d32e0ecf-f0a0-42a4-8a95-329435e6b9a5" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/8a9ea3b6-e9c0-4761-9289-4e588280fd7f" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/f331a851-d9f5-4c7a-8555-098b7062c122" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/5544f2c8-1905-4992-a882-14a709297324" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/757ad6ab-53da-4bb9-9556-1df35b2522b4" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/5992a909-fd7b-48fa-88be-1304eb8961f3" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/7d516904-d000-45ab-be8e-6c16f3a4592a" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/1d2e7bb9-b08c-4aa0-a080-63db1d458419" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/3509f079-cfb3-4a61-8314-b7b75f82eedc" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/59858ffc-dd22-454e-85ad-bc9ff4464b53" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/28d25768-4ac5-4ba2-ac78-be2d622289a1" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/40412b10-61f6-47ad-a462-401fc945bb23" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/6f929735-6fc1-4baa-a9ca-c5c588e08477" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/5687e0e1-c6f0-45b6-a9ab-4de6d0d3d09f" width="50%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/73309c89-d8a3-4245-802e-ea295713c269" width="50%">
</p>


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
