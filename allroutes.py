from flet import Page, View, Container,padding
from homeapp import HomeApp
from infomusic import InfoMusic


class AllRoutes:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigation(self, route):
        self.page.views.clear()
        
        if route == "/":
            self.page.views.append(
                View(
                    "/",
                    [
                        Container(
                            expand=True,
                            expand_loose=True,
                            bgcolor='#1f1f1f',
                            content=HomeApp(self.page).build(),
                        )
                    ],
                    padding=0
                )
            )
        elif route.startswith("/infomusic"):
            title = route.split("?title=")[-1] if "?title=" in route else None
            artist = route.split("?artist=")[-1] if "?artist=" in route else None
            
            info_music = InfoMusic(self.page)  
            if title:
                info_music.load_song_title(title,artist) 

            self.page.views.append(
                View(
                    "/infomusic",
                    [
                        Container(
                            expand=True,
                            expand_loose=True,
                            bgcolor='#1f1f1f',
                            content=info_music.build(),
                            padding=padding.all(10)
                        )
                    ],
                    padding=0
                )
            )

        self.page.go(route)
        self.page.update()

    @staticmethod
    def view_pop(page):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
            page.update()
