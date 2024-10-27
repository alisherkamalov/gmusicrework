import os
from flet import (
    Page, Row, Column, Text, border, padding,
    BoxShadow, IconButton, icons, Image, Container, MainAxisAlignment, border_radius, Slider, Audio
)
import yt_dlp
import asyncio

class InfoMusic:
    def __init__(self, page: Page):
        self.page = page
        self.song_title = None  
        self.song_artist = None
        self.audio_url = None
        self.loop = False
        self.is_playing = False
        self.audio_player = Audio(src='assets/audios/nonemusic.mp3', autoplay=False)
        self.loading_text = Text("")
        self.audio_dir = "assets/audios/"
        
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

    def load_song_title(self, title, artist):
        if '&artist=' in title:
            title = title.split('&artist=')[0]
        self.song_title = title.strip()
        self.song_artist = artist.strip() if artist else ""

    async def get_audio_url(self, title):
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True,
            'quiet': True,
        }
        print(f"Ищем аудио по названию: {title}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{title}", download=False)
                if 'entries' in info and info['entries']:
                    audio_url = info['entries'][0]['url']  
                    print(f"Найден URL: {audio_url}")  
                    return audio_url
                else:
                    print("Не найдено ни одной записи.")
        except Exception as e:
            print(f"Ошибка при получении URL: {e}")
        return None

    async def download_audio(self, url):
        self.loading_text.value = "Загрузка аудио, пожалуйста подождите..."
        self.page.update()  

        output_file = os.path.join(self.audio_dir, f"{self.song_title}.mp3")

        if os.path.exists(output_file) and output_file != os.path.join(self.audio_dir, "nonemusic.mp3"):
            os.remove(output_file)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.to_thread(ydl.download, [url])  
                self.audio_url = os.path.abspath(output_file)  
                print(f"Аудио загружено: {self.audio_url}")
        except Exception as e:
            print(f"Ошибка при загрузке аудио: {e}")

        self.loading_text.value = "Загрузка завершена. Воспроизведение..." 
        self.page.update() 


    async def toggle_play(self, e):
        """Переключаем воспроизведение/пауза."""
        if self.is_playing:
            self.is_playing = False
            print("Аудио остановлено.")
            self.audio_player.autoplay = False 
            self.loading_text.value = ""  
        else:
            if self.audio_url and os.path.exists(self.audio_url): 
                self.is_playing = True
                await self.play_audio()  
            else:
                await self.run_play_audio()

    async def play_audio(self):
        if self.audio_url and os.path.exists(self.audio_url):
            self.audio_player.src = f"{self.audio_dir}{self.song_title}.mp3"
            self.audio_player.autoplay = True
            print("Аудио воспроизведено.", os.path.join(self.audio_dir, f"{self.song_title}.mp3"))
            self.page.update()
        else:
            print("URL аудио не установлен или файл не найден.")

    def change_volume(self, e):
        volume = e.control.value
        print(f"Громкость изменена на: {volume}")
        self.audio_player.volume = volume / 100 

    async def run_play_audio(self):
        try:
            self.audio_url = await self.get_audio_url(self.song_title)
            if self.audio_url:
                await self.download_audio(self.audio_url)
                await self.play_audio() 
                self.is_playing = True
            else:
                print("Не удалось получить URL аудио.")
        except Exception as e:
            print(f"Ошибка при воспроизведении аудио: {e}")



    def toggle_loop(self, e):
        self.loop = not self.loop
        e.control.label = "Loop On" if self.loop else "Loop Off"


    def build(self):
        title_text = Text(self.song_title or "Название песни не указано", color='white', size=20)
        artist_text = Text(self.song_artist or "Автор песни не указан", color='gray', size=15)
        self.audio_player.volume = 0.5
        play_button = IconButton(
            icon=icons.PLAY_ARROW,
            icon_color='#31d26d',
            on_click=self.toggle_play 
        )

        loop_button = IconButton(
            icon=icons.LOOP,
            icon_color='#31d26d',
            on_click=self.toggle_loop
        )

        volume_slider = Slider(
            value=50,  
            min=0,
            max=100,
            label="Громкость",
            on_change=self.change_volume
        )

        return Container(
            expand=True,
            bgcolor='#1f1f1f',
            content=Column([
                self.audio_player,
                IconButton(
                    icon=icons.ARROW_BACK,
                    icon_color='#31d26d',
                    on_click=lambda e: self.page.go('/')
                ),
                Column([
                    Row([ 
                        Container(
                            width=200,
                            height=200,
                            border_radius=border_radius.all(10),
                            border=border.all(width=0.5, color='#4f4f4f'),
                            shadow=BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color='black'
                            ),
                            bgcolor='#1f1f1f',
                            content=Column([
                                Row([
                                    Image(src='assets/images/logo.png', width=100, height=100)
                                ], alignment=MainAxisAlignment.CENTER)
                                ], alignment=MainAxisAlignment.CENTER)
                        )
                    ], alignment=MainAxisAlignment.CENTER),
                    Container(
                        expand=True,
                        padding=padding.only(top=10),
                        content=Column([
                            title_text,
                            artist_text,
                            self.loading_text, 
                            Container(
                                expand=True,
                                padding=padding.only(top=15),
                                content=Row([
                                    play_button,
                                    loop_button
                                ])
                            ),
                            volume_slider  
                        ])
                    ),
                ])
            ])
        )
