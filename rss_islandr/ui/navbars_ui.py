import ttkbootstrap as tb


class HorizontalNavbar:
    def __init__(self, rel_height: float = 0.05, rel_width: float = 1.0):
        self.__rel_height = rel_height
        self.__rel_width = rel_width

    def __create_horizontal_navbar(self, parent_frame: tb.Frame) -> tb.Frame:
        """Create a horizontal navbar for the home page"""
        nav_bar_frame = tb.Frame(parent_frame)
        nav_bar_frame.place(relx=0, rely=0, relwidth=self.__rel_width, relheight=self.__rel_height)
        self.__frame_distances(nav_bar_frame)

        return nav_bar_frame

    def __create_child_frame(self, parent_frame: tb.Frame) -> tb.Frame:
        """Create a horizontal navbar for the home page"""
        child_frame = tb.Frame(parent_frame)
        child_frame.place(relx=0, rely=self.__rel_height, relwidth=self.__rel_width, relheight=1 - self.__rel_height)
        self.__frame_distances(child_frame)

        return child_frame

    def __frame_distances(self, frame) -> None:
        for i in range(1):
            frame.rowconfigure(i, weight=1)
        for i in range(12):
            frame.columnconfigure(i, weight=1)

    def __call__(self, parent_frame: tb.Frame):
        """
        Return
        """
        navbar_frame = self.__create_horizontal_navbar(parent_frame)
        child_frame = self.__create_child_frame(parent_frame)

        return navbar_frame, child_frame
