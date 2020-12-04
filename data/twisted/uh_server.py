#!/usr/bin/python3
# -*- coding: utf-8 -*-

from klein import run, route
from twisted.web.template import tags, slot
from klein import Klein, Plating

from input_handler import handle_input

app = Klein()

myStyle = Plating(
    tags=tags.html(
        tags.head(tags.title(slot("pageTitle"))),
        tags.body(tags.h1(slot("pageTitle"), Class="titleHeading"),
                  tags.div(slot(Plating.CONTENT)))
    )
)

@myStyle.routed(
    app.route("/input/"),
    tags.div())
def input(request):
	return {"r":['Hello, world!']}



if __name__ == '__main__':
	app.run("localhost", 8080)
    
