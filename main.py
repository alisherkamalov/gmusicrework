from flet import Page, app
from allroutes import AllRoutes


class GmusicApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.window.width = 500
        self.page.title = 'Gmusic'
        self.page.on_route_change = lambda e: AllRoutes(self.page).navigation(e.route)
        self.page.on_view_pop = AllRoutes(self.page).view_pop
        self.page.go('/')
        self.page.update()

app(target=GmusicApp)
