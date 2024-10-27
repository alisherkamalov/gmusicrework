from flet import (
    Page, Row, Column, Text, border, padding,
    BoxShadow, ListView, FontWeight, border_radius, TextField,
    MainAxisAlignment, Container, Animation, AnimationCurve,
    ProgressRing, IconButton,icons
)
import yt_dlp
import asyncio
import time


class HomeApp:
    def __init__(self, page: Page):
        self.page = page
        self.input = TextField(
            border='none',
            expand=True,
            hint_text='Что хочешь послушать?',
            color='white',
            cursor_color='#31d26d',
            on_change=self.on_input_change
        )
        self.active_music = None
        self.results_list = ListView(expand=True, controls=[])
        self.search_task = None

        self.loading_indicator = Container(
            expand=True,
            expand_loose=True,
            height=50,
            content=Column([
                Row([
                    ProgressRing(
                        width=16,
                        height=16,
                        bgcolor='#31d26d',
                        stroke_width=2
                    )
                ], alignment=MainAxisAlignment.CENTER)
            ], alignment=MainAxisAlignment.CENTER, expand=True)
        )

        self.search_button = IconButton(
            icon=icons.SEARCH,
            icon_color='#31d26d',
            on_click=self.start_search,
            disabled=True  
        )

    def on_item_click(self, item, title, artist):
        item.bgcolor = "white"
        self.page.update()
        time.sleep(0.1)
        item.bgcolor = "#1f1f1f"
        self.page.update()
        # Теперь передаем и имя исполнителя
        self.page.go(f'/infomusic?title={title}&artist={artist}') 
        self.page.update()




    async def on_input_change(self, e):
        input_text = self.input.value.strip()
        if input_text:
            self.search_button.disabled = False 
        else:
            self.search_button.disabled = True  
        self.page.update()

    async def delayed_search(self, query):
        self.results_list.controls.append(self.loading_indicator)
        self.page.update()

        await asyncio.sleep(1)  
        self.search_youtube(query)

        
        self.results_list.controls.remove(self.loading_indicator)
        self.page.update()

    def start_search(self, e):
        input_text = self.input.value.strip()
        if input_text:
            asyncio.run_coroutine_threadsafe(self.delayed_search(input_text), self.page.loop)

    def search_youtube(self, query):
        ydl_opts = {
            'noplaylist': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                self.results_list.controls.clear()  

                if info['entries']:
                    for entry in info['entries']:
                        # Извлечение названия и имени исполнителя
                        title = entry['title']
                        artist = entry.get('artist', 'Неизвестен')  # Попробуйте получить имя исполнителя, если доступно

                        item = Container(
                            content=Text(f"{title} - {artist}", color='white', size=20),  # Отображаем и название трека, и исполнителя
                            padding=10,
                            bgcolor="#1f1f1f",
                            margin=5,
                            animate=Animation(400, AnimationCurve.EASE),
                        )

                        # Передаем правильные аргументы в лямбда-функцию
                        item.on_click = lambda e, title=title, artist=artist: self.on_item_click(item, title, artist)  
                        self.results_list.controls.append(item)
                        self.active_music = title
                else:
                    self.results_list.controls.append(
                        Container(
                            content=Text("Нет результатов", color='white', size=20),
                            padding=10,
                            bgcolor="#1f1f1f",
                            margin=5,
                            animate=Animation(400, AnimationCurve.EASE),
                        )
                    )

                self.page.update()  

            except Exception as e:
                print(f"Ошибка при поиске: {e}")


    def build(self):
        return Container(
            expand=True,
            padding=padding.all(20.0),
            content=Column(
                controls=[
                    Text('Поиск трека', weight=FontWeight.W_500, size=30, color='white'),
                    Container(
                        expand=False,
                        height=50,
                        content=Row([self.input, self.search_button]),  
                        border_radius=border_radius.all(10),
                        padding=padding.only(left=10,right=10),
                        border=border.all(width=0.5, color='#4f4f4f'),
                        shadow=BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color='black'
                        ),
                        bgcolor='#1f1f1f'
                    ),
                    self.results_list
                ],
                expand=True,
            )
        )
