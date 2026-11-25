"""Keep a Tk game's artwork and controls in the same proportions as its window."""
import tkinter as tk


class GameCanvas(tk.Canvas):
    def __init__(self, root, width, height, bg):
        super().__init__(root, bg=bg, highlightthickness=0)
        root.configure(bg=bg)
        root.geometry(f"{width}x{height}")
        self.factor = 1
        self.styles, self.images = {}, {}
        self.place(relx=.5, rely=.5, anchor="center", width=width, height=height)

        def resize(factor):
            if factor == self.factor:
                return
            ratio = factor / self.factor
            self.scale("all", 0, 0, ratio, ratio)
            self.factor = factor
            self.place_configure(width=round(width * factor), height=round(height * factor))
            self.images.clear()
            for item in self.find_all():
                self._style(item)

        pending = None
        def queue_resize(event):
            nonlocal pending
            if event.widget is root:
                if pending is not None:
                    self.after_cancel(pending)
                pending = self.after(60, resize, min(event.width / width, event.height / height))

        root.bind("<Configure>", queue_resize, add="+")

    def _image(self, source):
        if self.factor == 1 or source in self.images:
            return self.images.get(source, source)

        # Copy columns, then rows, so transparent PNGs resize without extra packages.
        image = source
        for axis in (0, 1):
            w, h = (int(self.tk.call("image", dim, image)) for dim in ("width", "height"))
            length = (w, h)[axis]
            size = max(1, round(length * self.factor))
            out = tk.PhotoImage(master=self, width=size if axis == 0 else w,
                                height=h if axis == 0 else size)
            for dest in range(size):
                src = dest * length // size
                region = (src, 0, src+1, h) if axis == 0 else (0, src, w, src+1)
                target = (dest, 0) if axis == 0 else (0, dest)
                self.tk.call(out, "copy", image, "-from", *region, "-to", *target)
            image = out
        self.images[source] = image
        return image

    def _options_at_size(self, options):
        result = {}
        for key, value in options.items():
            if key == "image":
                result[key] = self._image(str(value))
            elif key == "font":
                family, size, *style = self.tk.splitlist(value)
                result[key] = (family, -max(1, round(abs(int(size)) * self.factor)), *style)
            else:
                result[key] = max(1, round(float(value) * self.factor))
        return result

    def _style(self, item):
        options, widget, widget_options = self.styles[item]
        if options:
            self.itemconfigure(item, **self._options_at_size(options))
        if widget:
            widget.configure(**self._options_at_size(widget_options))

    def _create(self, kind, args, options):
        item = super()._create(kind, [v * self.factor for v in args], options)
        widget = options.get("window")
        style = {k: v for k, v in options.items() if k in ("width", "height", "font", "image")}
        widget_style = {k: widget[k] for k in ("font", "image", "wraplength")
                        if widget and k in widget.keys() and str(widget[k]) not in ("", "0")}
        self.styles[item] = style, widget, widget_style
        self._style(item)
        return item

    def set_image(self, item, image):
        self.styles[item][0]["image"] = image
        self._style(item)

    def delete(self, *items):
        for tag in items:
            for item in self.find_withtag(tag):
                self.styles.pop(item, None)
        super().delete(*items)

    def coords(self, item, *points):
        return super().coords(item, *(v * self.factor for v in points))

    def move(self, item, dx, dy):
        super().move(item, dx * self.factor, dy * self.factor)
